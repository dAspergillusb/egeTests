from typing import Iterator
from sqlalchemy import (
    create_engine,
    Engine,
    Column,
    Integer,
    String,
    Boolean,
    Connection,
    ARRAY,
    Tuple
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from random import randint, choice

BASE = declarative_base()


class DailyStatistics(BASE):
    __tablename__: str = "daily_statistics"
    id: Column[Integer] = Column(Integer, primary_key=True)
    firstname: Column[String] = Column(String(100), nullable=False)
    lastname: Column[String] = Column(String(100), nullable=False)
    school_class: Column[String] = Column(String(4), nullable=False)
    test: Column[String] = Column(String)

    def __str__(self):
        return (
            f"DailyStatistics(id={self.id},"
            f" Name={self.firstname} {self.lastname},"
            f" class={self.school_class})"
            )

    def __repr__(self):
        return (
            f"DailyStatistics(id={self.id},"
            f" Name={self.firstname} {self.lastname},"
            f" class={self.school_class})"
            )


class DailyStatisticsDB:
    """
    Class creates or connects to database with statistics from different tests.
    """

    def __init__(self, db_name: str = "daily_statistics_db"):
        self.db_name = db_name
        self.engine = self._create_engine()
        BASE.metadata.create_all(self.engine)
        BASE.metadata.bind = self.engine
        self.db_session: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.session: Session = self.db_session()

    def _create_engine(self) -> Engine:
        db: Engine = create_engine(f"sqlite:///database/{self.db_name}.db")
        return db

    def _connect(self) -> Connection:
        db_connect: Connection = self.engine.connect()
        return db_connect

    def add_statistics(self, *, statistics_data: dict[str, str]) -> None:
        statistics: DailyStatistics = DailyStatistics(**statistics_data)
        self.session.add(statistics)
        self.session.commit()
        # self.session.close()

    # def change_statistics(self, id: int, data_to_change: dict[str, list[int]]) -> None:
    #     statistics: type[UsersStatistics] = self.session.query(UsersStatistics).get(id)
    #     for stat in statistics.to_dict():
    #         if data_to_change.get(stat):
    #             current_common_value, current_right_value, *_ = map(float, getattr(statistics, stat).split("&"))
    #             common_value, right_value = data_to_change.get(stat)
    #             # print(current_common_value, current_right_value, common_value, right_value)
    #             new_common_value = current_common_value + common_value
    #             new_right_value = current_right_value + right_value
    #             statistics.__setattr__(stat, "&".join([
    #                 f"{new_common_value}",
    #                 f"{new_right_value}",
    #                 f"{(new_right_value / new_common_value) * 100}",
    #             ]))
    #     self.session.commit()
    #     # self.session.close()


if __name__ == '__main__':
    daily: DailyStatisticsDB = DailyStatisticsDB()
    daily.add_statistics(statistics_data={
        "firstname": "Nikita",
        "lastname": "Zelentsov",
        "school_class": "11Z",
        "test": "$".join(("1", "2", "3", "4"))
    })
    print(DailyStatisticsDB().session.query(DailyStatistics).all()[0].test)