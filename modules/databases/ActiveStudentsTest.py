from typing import Iterator
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Engine,
    Column,
    Integer,
    String,
    Boolean,
    Connection,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from random import randint, choice

BASE = declarative_base()


class ActiveStudentsTest(BASE):
    __tablename__: str = "active_students_test"
    id: Column[Integer] = Column(Integer, primary_key=True)
    user_id: Column[Integer] = Column(Integer)
    stop_time: Column[Integer] = Column(Integer)
    test: Column[String] = Column(String)
    answers: Column[String] = Column(String)

    def __str__(self):
        return (
            f"ActiveStudentsTest(id={self.id},"
            f" user_id={self.user_id},"
            f" stop_time={self.stop_time},"
            f" test={self.test},"
            f" answers={self.answers})"
            )

    def __repr__(self):
        return (
            f"ActiveStudentsTest(id={self.id},"
            f" user_id={self.user_id},"
            f" stop_time={self.stop_time},"
            f" test={self.test},"
            f" answers={self.answers})"
            )

    def to_dict(self) -> dict[int, str]:
        answers_list: list[str] = self.answers.split("&")
        return {
            int(answer.split(":")[0]): answer.split(":")[-1] for answer in answers_list
        }

class ActiveStudentsTestDB:
    """
    Class creates or connects to database with statistics from different tests.
    """

    def __init__(self, db_name: str = "active_students_test_db"):
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

    def new_test_session(self, *, session_data: dict[str, str | int]) -> None:
        # print(session_data)
        test_length: int = len(session_data.get("test", "").split("&"))
        answers: list[str] = [f"{num}:0" for num in range(1, test_length + 1)]
        session_data["answers"] = "&".join(answers)
        test_session: ActiveStudentsTest = ActiveStudentsTest(**session_data)
        self.session.add(test_session)
        self.session.commit()
        # self.session.close()

    def remove_test_session(self, *, session_id: int) -> None:
        test_session: type[ActiveStudentsTest] = self.session.get(ActiveStudentsTest, session_id)
        self.session.delete(test_session)
        self.session.commit()

    def add_answer_to_test_session(self, *, session_id: int, q_num: str, answer: str) -> bool:
        _session: type[ActiveStudentsTest] | None = self.session.get(ActiveStudentsTest, session_id)
        if _session:
            questions_answers: list[str] = _session.answers.split("&")
            # questions_answers[questions_answers.index(f"{q_num}:")] = f"{q_num}:{answer}"
            for index, num in enumerate(questions_answers):
                if f"{q_num}:" in num:
                    questions_answers[index] = f"{q_num}:{answer}"
                    break
            _session.answers = "&".join(questions_answers)
            # print(_session.answers)
            self.session.commit()
            return True
        return False




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
        "test": "&".join(("1", "2", "3", "4"))
    })
    print(DailyStatisticsDB().session.query(DailyStatistics).all()[0].test)