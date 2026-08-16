from typing import Iterator
from datetime import datetime
from time import time
from sqlalchemy import (
    select,
    Result,
    Select,
    Integer,
    ForeignKey,
    String,
    TextClause,
    Sequence
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql.expression import text
from ..endpoints.config import DB_URL_PART, env_settings
# from .UsersDB import Users
from .MainDB import BASE_USERS
from ..errors.db_errors import NotMainDBNameError
from random import randint, choice


class ActiveStudentsTest(BASE_USERS):
    __tablename__: str = env_settings.ACTIVE_STUDENTS_TEST_DB_NAME
    ast_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{env_settings.USERS_DB_NAME}.user_id"))
    session_id: Mapped[str] = mapped_column(String, ForeignKey(f"{env_settings.USERS_SESSIONS_DB_NAME}.session_id", ondelete="CASCADE"))
    start_time: Mapped[int] = mapped_column(Integer, default=lambda: int(time()))
    stop_time: Mapped[int] = mapped_column(Integer)
    test: Mapped[dict[str, int]] = mapped_column(JSONB, default=dict)
    answers: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)

    def __str__(self):
        return (
            f"ActiveStudentsTest(id={self.ast_id},"
            f" user_id={self.user_id},"
            f" session_id={self.session_id},"
            f" stop_time={self.stop_time},"
            f" start_time={self.start_time},"
            f" test={self.test},"
            f" answers={self.answers})"
            )

    def __repr__(self):
        return (
            f"ActiveStudentsTest(id={self.ast_id},"
            f" user_id={self.user_id},"
            f" stop_time={self.stop_time},"
            f" test={self.test},"
            f" answers={self.answers})"
            )

    def to_dict(self) -> dict[int, str]:
        # answers_list: list[str] = self.answers.split("&")
        return {
            int(num): answer for num, answer in self.answers.items()
        }

class ActiveStudentsTestDB:
    """
    Class creates or connects to database with statistics from different tests.
    """

    def __init__(self, db_name: str | None):
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
        db: AsyncEngine = create_async_engine(f"{DB_URL_PART}{self.db_name}")
        return db

    async def init_db(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(BASE_USERS.metadata.create_all)
            print(f"Database initialized: {ActiveStudentsTest.__tablename__}")

    async def new_test_session(self, *, session_data: dict[str, str | float | int | dict[int, int]]) -> int:
        test_length: int = len(session_data.get("test", []))
        answers: dict[int, int] = {num: "0" for num in range(1, test_length + 1)}
        session_data["answers"] = answers
        async with self.session() as session:
            test_session: ActiveStudentsTest = ActiveStudentsTest(**session_data)
            session.add(test_session)
            await session.commit()
        return test_session.ast_id

    async def get_test_session(self, *, ast_id: int) -> type[ActiveStudentsTest] | None:
        if not ast_id:
            return None
        async with self.session() as session:
            return await session.get(ActiveStudentsTest, ast_id)

    async def get_all_test_sessions(self, join: type[BASE_USERS]) -> list[dict[str, str]]:
        async with self.session() as session:
            statement: Select[tuple[type[BASE_USERS], ActiveStudentsTest]] = select(join, ActiveStudentsTest).join(ActiveStudentsTest)
            result: Result[tuple[type[BASE_USERS], ActiveStudentsTest]] = await session.execute(statement)
            return [{
                "name": f"{user.firstname} {user.lastname}",
                "username": user.username,
                "rank": user.rank,
                "ast_id": session.ast_id,
                "start_time": session.start_time,
                "stop_time": session.stop_time,
                "test": session.test,
                "answers": session.answers,
                "expired": session.stop_time - int(time()) < 0
            } for user, session in result.all()]

    async def get_test_session_for_student(self, *, session_id: str) -> ActiveStudentsTest | None:
        async with self.session() as session:
            statement: Select[tuple[ActiveStudentsTest]] = select(ActiveStudentsTest).where(ActiveStudentsTest.session_id == session_id)
            result: Result[tuple[ActiveStudentsTest]] = await session.execute(statement)
            return result.scalars().first()

    async def remove_test_session(self, *, ast_id: int) -> None:
        async with self.session() as session:
            test_session: type[ActiveStudentsTest] | None = await session.get(ActiveStudentsTest, ast_id)
            if test_session:
                await session.delete(test_session)
                await session.commit()

    async def add_answer_to_test_session(self, *, ast_id: int, q_num: str, answer: list[str]) -> bool:
        async with self.session() as session:
            _session: type[ActiveStudentsTest] | None = await session.get(ActiveStudentsTest, ast_id)
            if _session:
                _session.answers[q_num] = "$".join(answer)
                flag_modified(_session, "answers")
                await session.commit()
                return True
        return False

    async def clear_table(self) -> None:
        async with self.session() as session:
            statement: TextClause = text(f"TRUNCATE TABLE {ActiveStudentsTest.__tablename__} RESTART IDENTITY;")
            try:
                await session.execute(statement)
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"While clearing table rise exception {e}")

    async def close_engine(self, db_name: str) -> None:
        await self.engine.dispose()
        del self.engine
        print(f"Pull of engine connection with {db_name} closed.")

