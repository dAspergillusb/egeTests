from typing import Iterator
from sqlalchemy import (
    create_engine,
    Engine,
    Column,
    Integer,
    String,
    Boolean,
    Connection
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from random import randint, choice

BASE = declarative_base()


class UsersStatistics(BASE):
    __tablename__: str = "statistics"
    id: Column[Integer] = Column(Integer, primary_key=True)
    firstname: Column[String] = Column(String(100), nullable=False)
    lastname: Column[String] = Column(String(100), nullable=False)
    school_class: Column[String] = Column(String(4), nullable=False)
    q_type_1: Column[String] = Column(String(100))
    q_type_2: Column[String] = Column(String(100))
    q_type_3: Column[String] = Column(String(100))
    q_type_4: Column[String] = Column(String(100))
    q_type_5: Column[String] = Column(String(100))
    q_type_6: Column[String] = Column(String(100))
    q_type_7: Column[String] = Column(String(100))
    q_type_8: Column[String] = Column(String(100))
    q_type_9: Column[String] = Column(String(100))
    q_type_10: Column[String] = Column(String(100))
    q_type_11: Column[String] = Column(String(100))
    q_type_12: Column[String] = Column(String(100))
    q_type_13: Column[String] = Column(String(100))
    q_type_14: Column[String] = Column(String(100))
    q_type_15: Column[String] = Column(String(100))
    q_type_16: Column[String] = Column(String(100))
    q_type_17: Column[String] = Column(String(100))
    q_type_18: Column[String] = Column(String(100))
    q_type_19: Column[String] = Column(String(100))
    q_type_20: Column[String] = Column(String(100))
    q_type_21: Column[String] = Column(String(100))
    q_type_22: Column[String] = Column(String(100))
    q_type_23: Column[String] = Column(String(100))
    q_type_24: Column[String] = Column(String(100))
    q_type_25: Column[String] = Column(String(100))
    q_type_26: Column[String] = Column(String(100))
    q_type_27: Column[String] = Column(String(100))

    def __str__(self):
        return (
            f"UserStatistics(id={self.id},"
            f" Name={self.firstname} {self.lastname},"
            f" class={self.school_class})"
            )

    def __repr__(self):
        return (
            f"UserStatistics(id={self.id},"
            f" Name={self.firstname} {self.lastname},"
            f" class={self.school_class})"
            )

    def __iter__(self) -> Iterator:
        q_types: dict[str, Column[String]] = self.to_dict()
        for item in q_types:
            yield q_types[item]

    def to_dict(self) -> dict[str, Column[String]]:
        return {
            "q_type_1": self.q_type_1,
            "q_type_2": self.q_type_2,
            "q_type_3": self.q_type_3,
            "q_type_4": self.q_type_4,
            "q_type_5": self.q_type_5,
            "q_type_6": self.q_type_6,
            "q_type_7": self.q_type_7,
            "q_type_8": self.q_type_8,
            "q_type_9": self.q_type_9,
            "q_type_10": self.q_type_10,
            "q_type_11": self.q_type_11,
            "q_type_12": self.q_type_12,
            "q_type_13": self.q_type_13,
            "q_type_14": self.q_type_14,
            "q_type_15": self.q_type_15,
            "q_type_16": self.q_type_16,
            "q_type_17": self.q_type_17,
            "q_type_18": self.q_type_18,
            "q_type_19": self.q_type_19,
            "q_type_20": self.q_type_20,
            "q_type_21": self.q_type_21,
            "q_type_22": self.q_type_22,
            "q_type_23": self.q_type_23,
            "q_type_24": self.q_type_24,
            "q_type_25": self.q_type_25,
            "q_type_26": self.q_type_26,
            "q_type_27": self.q_type_27
        }


class UsersStatisticsDB:
    """
    Class creates or connects to database with statistics from different tests.
    """

    def __init__(self, db_name: str = "users_statistics_db"):
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
        statistics: UsersStatistics = UsersStatistics(**statistics_data)
        self.session.add(statistics)
        self.session.commit()
        # self.session.close()

    def change_statistics(self, id: int, data_to_change: dict[str, list[int]]) -> None:
        statistics: type[UsersStatistics] = self.session.query(UsersStatistics).get(id)
        for stat in statistics.to_dict():
            if data_to_change.get(stat):
                current_common_value, current_right_value, *_ = map(float, getattr(statistics, stat).split("&"))
                common_value, right_value = data_to_change.get(stat)
                # print(current_common_value, current_right_value, common_value, right_value)
                new_common_value = current_common_value + common_value
                new_right_value = current_right_value + right_value
                statistics.__setattr__(stat, "&".join([
                    f"{new_common_value}",
                    f"{new_right_value}",
                    f"{(new_right_value / new_common_value) * 100}",
                ]))
        self.session.commit()
        # self.session.close()


if __name__ == '__main__':
    statistics: UsersStatisticsDB = UsersStatisticsDB()
    nums: list[str] = [f"{num}" for num in range(5, 12)]
    letters: list[str] = ["А", "Б", "В"]
    school_classes: list[str] = sorted(
        [
            f"{num}-{letter}" for letter in letters for num in nums
        ],
        key=lambda sc: int(sc.split("-")[0]
                           )
    )
    for school_class in school_classes:
        for _ in range(1000):
            common_value = randint(0, randint(50, 80))
            statistics.add_statistics(
                username="Kristy",
                subject="mathematics",
                school_class=school_class,
                common_value=common_value,
                common_not_right=100 - common_value,
                common_max_value=100,
                common_percent=common_value,
                test_date=f"2024-11-{randint(1, 30)}"
            )

