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
    subject: Column[String] = Column(String(15), nullable=False)
    firstname: Column[String] = Column(String(100), nullable=False)
    lastname: Column[String] = Column(String(100), nullable=False)
    user_id: Column[String] = Column(Integer, nullable=False)
    school_class: Column[String] = Column(String(4), nullable=False)
    common_value: Column[Integer] = Column(Integer)
    common_max_value: Column[Integer] = Column(Integer)
    common_not_right: Column[Integer] = Column(Integer)
    common_percent: Column[Integer] = Column(Integer)
    test_date: Column[String] = Column(String(20))

    def __str__(self):
        return (
            f"UserStatistics(id={self.id},"
            f" user_id={self.user_id},"
            f" class={self.school_class},"
            f" subject={self.subject}, "
            f" common_value={self.common_value},"
            f" common_max_value={self.common_max_value},"
            f" common_not_right={self.common_not_right},"
            f" common_percent={self.common_percent},"
            f" test_date={self.test_date})"
            )

    def __repr__(self):
        return (
            f"UserStatistics(id={self.id},"
            f" user_id={self.user_id},"
            f" class={self.school_class},"
            f" subject={self.subject}, "
            f" common_value={self.common_value},"
            f" common_max_value={self.common_max_value},"
            f" common_not_right={self.common_not_right},"
            f" common_percent={self.common_percent},"
            f" test_date={self.test_date})"
            )


class UsersStatisticsDB:
    """
    Class creates or connects to database with statistics from different tests.
    """

    def __init__(self, db_name: str = "users_statistics_db"):
        self.db_name = db_name
        self.engine = self._create_engine()
        BASE.metadata.create_all(self.engine)
        BASE.metadata.bind = self.engine
        self.db_session: sessionmaker[[Session]] = sessionmaker(bind=self.engine)
        self.session: Session = self.db_session()

    def _create_engine(self) -> Engine:
        db: Engine = create_engine(f"sqlite:///database/{self.db_name}.db")
        return db

    def _connect(self) -> Connection:
        db_connect: Connection = self.engine.connect()
        return db_connect

    def add_statistics(self, *, subject: str, common_value: int, common_max_value: int, school_class: str,
                       common_not_right: int, common_percent: int, test_date: str, user_id: int,
                       firstname: str, lastname: str) -> None:
        statistics: UsersStatistics = UsersStatistics(
            subject=subject,
            user_id=user_id,
            firstname=firstname,
            lastname=lastname,
            school_class=school_class,
            common_value=common_value,
            common_max_value=common_max_value,
            common_not_right=common_not_right,
            common_percent=common_percent,
            test_date=test_date
        )
        self.session.add(statistics)
        self.session.commit()


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

