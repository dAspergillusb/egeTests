from asyncio import CancelledError
from uuid import uuid4
from datetime import datetime, timezone, timedelta, tzinfo

from fastapi import HTTPException
from sqlalchemy import (
    Select,
    Result,
    select,
    Integer,
    ForeignKey,
    String,
    DateTime,
    Sequence,
    Any
)
from sqlalchemy.exc import IntegrityError, OperationalError, DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from starlette import status

from ..databases.UsersDB import Users
from ..endpoints.config import DB_URL_PART, env_settings
from .MainDB import BASE_USERS
from ..errors.db_errors import NotMainDBNameError


class UserSessions(BASE_USERS):
    __tablename__: str = env_settings.USERS_SESSIONS_DB_NAME
    session_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{env_settings.USERS_DB_NAME}.user_id"))
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    session_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    expire_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= lambda: datetime.now(tz=timezone.utc) + timedelta(days=2))


class UserSessionsDB:

    def __init__(self, db_name: str | None) -> None:
        if not db_name:
            raise NotMainDBNameError()
        self.db_name = db_name
        self.engine = self._create_engine()
        self.session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def _create_engine(self) -> AsyncEngine:
        return create_async_engine(f"{DB_URL_PART}{self.db_name}")

    async def init_db(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(BASE_USERS.metadata.create_all)
            print(f"Database initialized: {UserSessions.__tablename__}")

    async def session_id_exists(self, session_id: str) -> bool:
        async with self.session() as session:
            return True if await session.get(UserSessions, session_id) else False

    async def create_new_session(self, user_id: int, user_agent: str, ip_address: str, session_id: str | None = None) -> str:
        async with self.session() as session:
            new_session: UserSessions = UserSessions(
                session_id=session_id,
                user_id=user_id,
                user_agent=user_agent,
                ip_address=ip_address
            )
            session.add(new_session)
            await session.commit()
        return new_session.session_id

    async def get_session(self, session_id: str = "", user_id: int = 0) -> type[UserSessions] | None:
        async with self.session() as session:
            if session_id:
                current_session: type[UserSessions] | None = await session.get(UserSessions, session_id)
                return current_session
            if user_id:
                statement: Select[tuple[UserSessions]] = select(UserSessions).where(UserSessions.user_id == user_id)
                result: Result[tuple[UserSessions]] = await session.execute(statement)
                return result.scalar_one_or_none()
        return None

    async def get_active_sessions(self, *, current_session_id: str = "") -> list[dict[str, Any]]:
        async with self.session() as session:
            statement = select(Users, UserSessions).join(UserSessions)
            result = await session.execute(statement)

            return [{
                "user_id": user.user_id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "username": user.username,
                "session_id": session.session_id,
                "user_agent": session.user_agent,
                "ip_address": session.ip_address,
                "session_date": session.session_date,
                "expire_date": session.expire_date,
                "expired": True if session.expire_date < datetime.now(tz=timezone.utc) else False,
                "is_current_session": True if current_session_id == session.session_id else False
            } for user, session in result.all()]

    async def delete_session(self, session_id: str = "", user_id: int = 0) -> None | HTTPException:
        current_session: type[UserSessions] | None = await self.get_session(session_id, user_id)
        if current_session:
            async with self.session() as session:
                await session.delete(current_session)
                # try:
                await session.commit()
                # except IntegrityError as error:
                #     await session.rollback()
                #     print(f"While executing there is an error: {error.detail}")
                #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.detail)
                # except OperationalError as error:
                #     await session.rollback()
                #     print(f"While executing there is an error: {error.detail}")
                #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.detail)
                # except DBAPIError as error:
                #     await session.rollback()
                #     print(f"While executing there is an error: {error.detail}")
                #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.detail)
                # except CancelledError as error:
                #     await session.rollback()
                #     print(f"While executing there is an error: {error}")
                #     return

    async def close_engine(self, db_name: str) -> None:
        await self.engine.dispose()
        del self.engine
        print(f"Pull of engine connection with {db_name} closed.")