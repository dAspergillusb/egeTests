from asyncio import CancelledError
from functools import singledispatchmethod
from sqlalchemy import (
    select,
    Result,
    Integer,
    String,
    Boolean,
    Select,
    text,
    Sequence,
    TextClause
)
from sqlalchemy.exc import OperationalError, DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)
from starlette import status

from .._types.Types import Ranks
from ..endpoints.config import env_settings, DB_URL_PART
from sqlalchemy.orm import Mapped, mapped_column
from .MainDB import BASE_USERS
from .UsersStatisticsDB import UsersStatisticsDB
from .ActiveStudentsTest import ActiveStudentsTestDB
from .DailyStatisticsDB import DailyStatisticsDB
from ..errors.db_errors import NotMainDBNameError


class Users(BASE_USERS):
    __tablename__ = env_settings.USERS_DB_NAME
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String, nullable=False)
    lastname: Mapped[str] = mapped_column(String, nullable=False)
    sex: Mapped[str] = mapped_column(String, nullable=False)
    school_class: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    rank: Mapped[str] = mapped_column(String, default="student")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __contains__(self, item: str):
        return self.username == item

    def __str__(self):
        return f"User: {self.user_id=}, {self.username=}"

    def __repr__(self):
        return f"( User: {self.user_id=}, {self.username=} , {self.rank=}) "


class UsersDB:

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
            print(f"Database initialized: {Users.__tablename__}")

    async def get_all_users(self) -> Sequence[Users]:
        async with self.session() as session:
            query: Select[tuple[Users]] = select(Users)
            result: Result[tuple[Users]] = await session.execute(query)
            return result.scalars().all()

    async def exist_username(self, username: str | Mapped[str]) -> bool:
        async with self.session() as session:
            query: Select[tuple[Users]] = select(Users).where(Users.username == username)
            result: Result[tuple[Users]] = await session.execute(query)
            return bool(result.scalars().first())

    async def choose_user(self, **user_data) -> type[Users] | None:
        async with self.session() as session:
            if "user_id" in user_data:
                return await session.get(Users, user_data["user_id"])
            query: Select[tuple[Users]] = select(Users).where(Users.username == user_data["username"])
            result: Result[tuple[Users]] = await session.execute(query)
            return result.scalars().first()

    async def choose_users_by_rank(self, rank: str = "student") -> tuple[type[Users] | None]:
        async with self.session() as session:
            query: Select[tuple[Users]] = select(Users).where(Users.rank == rank)
            result = await session.execute(query)
            return tuple(result.scalars().all())

    @singledispatchmethod
    async def add_user(self, user_data) -> bool | int | Users:
        print(f"This type of user_data ({type(user_data)} does not support!")
        return False

    @add_user.register
    async def _(self, user_data: Users) -> bool | int:
        user_exists: bool = await self.exist_username(user_data.username)
        if user_exists:
            return False
        del user_data.user_id
        async with self.session() as session:
            print(user_data.__dict__)
            new_user: Users = Users(**{k: v for k, v in user_data.__dict__.items() if not k.startswith("_")})
            session.add(new_user)
            try:
                await session.commit()
            except IntegrityError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            except OperationalError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            except DBAPIError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            except CancelledError as error:
                await session.rollback()
                print(f"While executing there is an error: {error}")
                return False
            return new_user.user_id

    @add_user.register
    async def _(self, user_data: dict) -> bool | Users:
        user_exists: bool = await self.exist_username(user_data.get("username", ""))
        if user_exists:
            return False
        async with self.session() as session:
            new_user: Users = Users(**user_data)
            session.add(new_user)
            await session.commit()
            if new_user.rank == Ranks.STUDENT:
                statistics_db: UsersStatisticsDB = UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME)
                await statistics_db.add_statistics(
                    statistics_data={"user_id": new_user.user_id}
                )
                # print(f"User {new_user.user_id}:{new_user.username}:{stat.user_id}")
        return new_user

    async def change_user_data(self, *, data_to_change: dict[str, str | int], user_id: int | None = None) -> bool:
        user: type[Users] | None = None
        if user_id:
            user = await self.choose_user(user_id=user_id)
        elif data_to_change.get("username"):
            user = await self.choose_user(username=data_to_change.pop("username"))

        async with self.session() as session:
            if user:
                for data, value in data_to_change.items():
                    if any((
                        value,
                        isinstance(value, bool),
                    )):
                        user.__setattr__(data, value)
                session.add(user)
                await session.commit()
                return True
        return False

    async def delete_user(self, user_id: Mapped[int] | int) -> bool | int:
        user: type[Users] | None = await self.choose_user(user_id=user_id)
        if user:
            if user.rank == Ranks.STUDENT:
                await UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).delete_statistics(user_id=user_id)
            if user.rank == Ranks.ADMIN:
                admins_count: int = len(await self.choose_users_by_rank(rank="admin"))
                if admins_count < 2:
                    return status.HTTP_403_FORBIDDEN
            async with self.session() as session:
                await session.delete(user)
                try:
                    await session.commit()
                except IntegrityError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                except OperationalError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                except DBAPIError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                except CancelledError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                return True
        return status.HTTP_404_NOT_FOUND

    async def clear_table(self) -> int | None:
        async with self.session() as session:
            statement: TextClause = text(f"TRUNCATE TABLE {Users.__tablename__} RESTART IDENTITY CASCADE;")
            try:
                await session.execute(statement)
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"While clearing table rise exception {e}")
                return status.HTTP_400_BAD_REQUEST
        await UsersStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).clear_table()
        await DailyStatisticsDB(db_name=env_settings.MAIN_DB_USERS_NAME).clear_table()
        await ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME).clear_table()

    async def close_engine(self, db_name: str) -> None:
        await self.engine.dispose()
        del self.engine
        print(f"Pull of engine connection with {db_name} closed.")



if __name__ == '__main__':
    database = UsersDB()
    # user = database.session.query(Users).filter(Users.username == "millerma").first()
    # print(user)
    # user.password = generate_code_from_password("3Miller#Maria3")
    # database.session.commit()
    # database.session.close()
    # database.add_instance(
    #     user_data={
    #         "firstname": "Мария",
    #         "lastname": "Миллер",
    #         "sex": "жен",
    #         "school_class": "",
    #         "username": "millerma",
    #         "password": "3Miller#Maria3",
    #         "rank": "teacher"
    # })
    #database.delete_instance(user_id=23)
    #database.change_instance(user_id=22, subject="английский язык")

    # for some_user in database.session.query(Users).all():
    #     print(f"{some_user.user_id=}::{some_user.username=}::{some_user.firstname=}::{some_user.lastname=}::{some_user.rank=}::{some_user.sex=}::{some_user.password=}::{some_user.school_class=}")


