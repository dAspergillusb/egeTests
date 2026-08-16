from collections.abc import Sequence
from typing import Iterator, Any
from fastapi import HTTPException
from sqlalchemy import (
    select,
    Result,
    Integer,
    String,
    Select,
    ForeignKey,
    or_,
    and_,
    Row,
    TextClause
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import text
from ..endpoints.config import DB_URL_PART, env_settings
from .MainDB import BASE_USERS
from ..errors.db_errors import NotMainDBNameError


class UsersStatistics(BASE_USERS):
    __tablename__: str = env_settings.USERS_STATISTICS_DB_NAME
    us_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{env_settings.USERS_DB_NAME}.user_id"))
    for i in range(1, 28):
        locals()[f"q_type_{i}"]: Mapped[str] = mapped_column(String, default="0.0&0.0&0.0")

    def __str__(self):
        return (
            f"UserStatistics(id={self.us_id},"
            f" UserID={self.user_id},"
            f" q_type_1={self.q_type_1})"
            )

    def __repr__(self):
        return (
            f"UserStatistics(id={self.us_id},"
            f" UserID={self.user_id},"
            f" q_type_1={self.q_type_1},"
            f" q_type_2={self.q_type_2},"
            f" q_type_3={self.q_type_3},...)"
            )

    def __iter__(self) -> Iterator[Mapped[str]]:
        return iter(self.to_dict().values())

    def to_dict(self) -> dict[str, Mapped[str]]:
        return {
            attr: getattr(self, attr)
            for attr in dir(self)
            if attr.startswith("q_type_")
        }


class UsersStatisticsDB:
    """
    Class connects to database with statistics from different tests.
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
            print(f"Database initialized: {UsersStatistics.__tablename__}")

    async def get_statistics_by_id(self, *, statistics_id: int) -> type[UsersStatistics] | None:
        async with self.session() as session:
            statistics: type[UsersStatistics] | None = await session.get(UsersStatistics, statistics_id)
            return statistics

    async def get_statistics_by_userid(self, *, user_id: int | None) -> UsersStatistics:
        async with self.session() as session:
            query: Select[tuple[UsersStatistics]] = select(UsersStatistics).where(UsersStatistics.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().first()

    async def get_all_statistics(
            self,
            *,
            join = None
    ) -> Sequence[UsersStatistics] | Sequence[Row[Any]]:
        async with self.session() as session:
            if join:
                statement = select(join, UsersStatistics).join(UsersStatistics)
                all_user_statistics = await session.execute(statement)
                return all_user_statistics.all()
            else:
                statement = select(UsersStatistics)
                all_user_statistics: Result[tuple[UsersStatistics]] = await session.execute(statement)
                return all_user_statistics.scalars().all()

    async def add_statistics(self, *, statistics_data: dict[str, str | int]) -> None:
        async with self.session() as session:
            statistics: UsersStatistics = UsersStatistics(**statistics_data)
            session.add(statistics)
            await session.commit()
        return statistics

    async def change_statistics(self, *, data_to_change: dict[str, list[int]], user_id: int = 0, us_id: int = 0) -> None:
        statistics: type[UsersStatistics] | None = None
        if user_id:
            statistics = await self.get_statistics_by_userid(user_id=user_id)

        async with self.session() as session:
            if us_id:
                statistics = await session.get(UsersStatistics, us_id)
            if not statistics:
                print("There is no statistics object")
                return None
            # print(statistics)
            dict_from_statistics: dict[str, Mapped[str]] = statistics.to_dict()
            for stat in dict_from_statistics:
                if data_to_change.get(stat):
                    current_common_value, current_right_value, *_ = map(float, getattr(statistics, stat).split("&"))
                    common_value, right_value = data_to_change.get(stat)
                    new_common_value = current_common_value + common_value
                    new_right_value = current_right_value + right_value
                    percentage = (new_right_value / new_common_value) * 100 if new_common_value > 0 else 0.0
                    setattr(statistics, stat, f"{new_common_value}&{new_right_value}&{percentage}")
            session.add(statistics)
            await session.commit()
            # print(await self.get_statistics_by_id(statistics.us_id))
        return None

    async def delete_statistics(self, *, user_id: int = 0, us_id: int = 0) -> bool:
        statistics: type[UsersStatistics] | None = None
        if us_id:
            statistics = await self.get_statistics_by_id(statistics_id=us_id)
        if user_id:
            statistics = await self.get_statistics_by_userid(user_id=user_id)
        if not statistics:
            raise HTTPException(status_code=404, detail="Statistics not found")

        async with self.session() as session:
            await session.delete(statistics)
            await session.commit()
            return True

    async def clear_table(self) -> None:
        async with self.session() as session:
            statement: TextClause = text(f"TRUNCATE TABLE {UsersStatistics.__tablename__} RESTART IDENTITY;")
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

if __name__ == '__main__':
    statistics_: UsersStatisticsDB = UsersStatisticsDB()
    # nums: list[str] = [f"{num}" for num in range(5, 12)]
    # letters: list[str] = ["А", "Б", "В"]
    # school_classes: list[str] = sorted(
    #     [
    #         f"{num}-{letter}" for letter in letters for num in nums
    #     ],
    #     key=lambda sc: int(sc.split("-")[0]
    #                        )
    # )
    # for school_class in school_classes:
    #     for _ in range(1000):
    #         common_value = randint(0, randint(50, 80))
    #         statistics.add_statistics(
    #             username="Kristy",
    #             subject="mathematics",
    #             school_class=school_class,
    #             common_value=common_value,
    #             common_not_right=100 - common_value,
    #             common_max_value=100,
    #             common_percent=common_value,
    #             test_date=f"2024-11-{randint(1, 30)}"
    #         )

