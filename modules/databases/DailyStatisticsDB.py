from collections.abc import Sequence, Generator
from collections import defaultdict
from typing import Iterator
from datetime import datetime
from sqlalchemy import (
    select,
    Result,
    Select,
    Integer,
    String,
    ForeignKey,
    TextClause,
    Float
)
from sqlalchemy.dialects.postgresql import JSONB
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
from .InformaticsDB import Informatics, InformaticsDB
from ..errors.db_errors import NotMainDBNameError


class DailyStatistics(BASE_USERS):
    __tablename__: str = env_settings.DAILY_STATISTICS_DB_NAME
    ds_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{env_settings.USERS_DB_NAME}.user_id"))
    test: Mapped[str] = mapped_column(String)
    result: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String, default=lambda: datetime.now().isoformat(sep="&", timespec="minutes"))
    test_time: Mapped[int] = mapped_column(Integer)
    problem_type_intervals: Mapped[dict[str, int]] = mapped_column(JSONB, default=dict)
    easy_accuracy: Mapped[float] = mapped_column(Float)
    programming_accuracy: Mapped[float] = mapped_column(Float)
    hard_accuracy: Mapped[float] = mapped_column(Float)
    final_result: Mapped[int] = mapped_column(Integer)

    def __str__(self):
        return (
            f"DailyStatistics(id={self.ds_id},"
            f" Test={self.test},"
            f" Result={self.result},"
            f" date={self.date})"
            )

    def __repr__(self):
        return (
            f"DailyStatistics(id={self.ds_id},"
            f" Test={self.test},"
            f" Result={self.result},"
            f" date={self.date})"
            )


class DailyStatisticsDB:
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
            print(f"Database initialized: {DailyStatistics.__tablename__}")

    async def add_statistics(self, *, statistics_data: dict[str, str | int | float]) -> None:
        async with self.session() as session:
            statistics = DailyStatistics(**statistics_data)
            session.add(statistics)
            await session.commit()

    async def get_daily_statistics_for_student(self, *, user_id: int) -> tuple[dict[str, defaultdict[str, list[type[Informatics]]]], dict[str, float ]]:
        if not user_id:
            return {}, {}
        async with self.session() as session:
            statement: Select[tuple[DailyStatistics]] = select(DailyStatistics).where(DailyStatistics.user_id == user_id)
            result: Result[tuple[DailyStatistics]] = await session.execute(statement)
            student_raw_daily_statistics: Sequence[DailyStatistics] = result.scalars().all()

        easy_accuracies: list[float] = []
        programming_accuracies: list[float] = []
        hard_accuracies: list[float] = []
        test_times: list[int] = []
        final_results: list[int] = []
        student_daily_statistics: dict[str, defaultdict[str, list[type[Informatics]]]] = {}
        for daily_stat in student_raw_daily_statistics:
            easy_accuracies.append(daily_stat.easy_accuracy)
            programming_accuracies.append(daily_stat.programming_accuracy)
            hard_accuracies.append(daily_stat.hard_accuracy)
            test_times.append(daily_stat.test_time)
            final_results.append(daily_stat.final_result)
            year_month_day, hours_minutes = daily_stat.date.split("&")
            old_variant: list[type[Informatics] | None] = [await InformaticsDB(
                db_name=self.db_name
            ).get_question(q_id=q_id) for q_id in map(int, daily_stat.test.split("&"))]
            if not student_daily_statistics.get(year_month_day):
                student_daily_statistics[year_month_day] = defaultdict(list)
            student_daily_statistics[year_month_day][hours_minutes].extend(old_variant)
        accuracies: dict[str, float] = {
            "average_easy_accuracy": sum(easy_accuracies) / len(easy_accuracies) if easy_accuracies else 0,
            "average_programming_accuracy": sum(programming_accuracies) / len(programming_accuracies) if programming_accuracies else 0,
            "average_hard_accuracy": sum(hard_accuracies) / len(hard_accuracies) if hard_accuracies else 0,
            "average_test_time": sum(test_times) / len(test_times) if test_times else 0,
            "average_final_result": sum(final_results) / len(final_results) if final_results else 0,
        }
        return student_daily_statistics, accuracies

    async def get_old_test(self, date: str) -> tuple[dict[int, type[Informatics] | None], dict[int, int]] | None:
        async with self.session() as session:
            statement: Select[tuple[DailyStatistics]] = select(DailyStatistics).where(DailyStatistics.date == date)
            result: Result[tuple[DailyStatistics]] = await session.execute(statement)
            old_test_ids_daily_statistics: type[DailyStatistics] | None = result.scalars().first()
        if old_test_ids_daily_statistics:
            old_test: dict[int, type[Informatics] | None] = {
                num: await InformaticsDB(
                    db_name=env_settings.MAIN_DB_INFORMATICS_NAME
                ).get_question(q_id=q_id) for num, q_id in
                enumerate(map(int, old_test_ids_daily_statistics.test.split("&")), start=1)
            }
            old_results: dict[int, int] = {
                num: result for num, result in
                enumerate(map(int, old_test_ids_daily_statistics.result.split("&")), start=1)
            }
            return old_test, old_results
        return None

    async def clear_table(self) -> None:
        async with self.session() as session:
            statement: TextClause = text(f"TRUNCATE TABLE {DailyStatistics.__tablename__} RESTART IDENTITY;")
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
