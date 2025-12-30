from os import mkdir
from sqlalchemy import (
    create_engine,
    Engine,
    Column,
    Integer,
    String,
    Connection
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from modules._types.Types import DataBase


BASE = declarative_base()


class Informatics(BASE):
    """
    class base of table for database with questions for Informatics subject.
    """
    __tablename__: str = "informatics"
    id: Column[Integer] = Column(Integer, primary_key=True)
    q_number: Column[Integer] = Column(Integer, nullable=False)
    q_school_class: Column[String] = Column(String(4), nullable=False)
    q_text: Column[String] = Column(String(250))
    q_difficulty: Column[String] = Column(String(250))
    q_files: Column[String] = Column(String(250))
    q_right_answer: Column[String] = Column(String(50), nullable=False)

    def __str__(self):
        return f"Informatics(\nid={self.id},\nnumber={self.q_number},\nclass={self.q_school_class}\n,answer={self.q_right_answer}\n)\n"

    def __repr__(self):
        return f"Informatics(\nid={self.id},\nq_number={self.q_number},\n" + \
                f"school_class={self.q_school_class}\n)\n"

    def get_question(self) -> dict[str, Column[String] | Column[Integer]]:
        return {
            "id": self.id,
            "q_number": self.q_number,
            "q_school_class": self.q_school_class,
            "q_text": self.q_text,
            "q_difficulty": self.q_difficulty,
            "q_files": self.q_files,
            "q_right_answer": self.q_right_answer
        }


class InformaticsDB(DataBase):
    """
    Class creates or connects to database with questions for tests with Informatics subject. Class can create new question
    in database.
    """
    def __init__(self, db_name: str = "informatics_db"):
        self.db_name = db_name
        self.engine = self._create_engine()
        BASE.metadata.create_all(self.engine)
        BASE.metadata.bind = self.engine
        self.db_session: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.session: Session = self.db_session()

    def _create_engine(self) -> Engine:
        try:
            mkdir("database")
        except FileExistsError:
            pass
        finally:
            db: Engine = create_engine(f"sqlite:///database/{self.db_name}.db")
        return db

    def _connect(self) -> Connection:
        db_connect: Connection = self.engine.connect()
        return db_connect

    def add_question(self, *, question_data: dict[str, str | int]) -> None:
        question: Informatics = Informatics(
            q_number=question_data.get("q_number"),
            q_text=question_data.get("q_text"),
            q_difficulty=question_data.get("q_difficulty"),
            q_school_class=question_data.get("q_school_class"),
            q_files=question_data.get("q_files"),
            q_right_answer=question_data.get("q_right_answer")
        )
        self.session.add(question)
        self.session.commit()

    def change_question(self, *, question_id: str, data: dict[str, Column[String] | str]) -> None:
        question: Informatics = self.session.query(Informatics).get(question_id)
        question.q_title = data.get("q_title")
        question.q_text = data.get("q_text")
        question.files = data.get("q_files")
        question.q_right_answer = data.get("q_right_answer")
        self.session.commit()


if __name__ == '__main__':
    _question = InformaticsDB()
    for num in range(100):
        _question.add_question(question_data={
            "q_number": num,
            "q_text": f"Problem_{num}",
            "q_school_class": "11Б",
            "q_files": "Solute_problem_{num}",
            "q_right_answer": "9-Б"
        }
        )
    """for question_num in range(21):
        print(_question.session.query(Informatics).all()[question_num].question_name)"""
