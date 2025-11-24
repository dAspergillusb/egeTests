from abc import ABC, abstractmethod
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session


BASE: declarative_base = declarative_base()


class DataBase(ABC):
    session: Session

    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def _create_engine(self): pass

    @abstractmethod
    def _connect(self): pass

    @abstractmethod
    def add_question(self, *, question_data: dict[str, str | int]) -> None: pass

    @abstractmethod
    def change_question(self, *, question_id: str, data: dict[str, str | int]) -> None: pass


class BaseTable(BASE):

    __tablename__ = "base_table"
    id: Column[Integer] = Column(Integer, primary_key=True)
    q_number: Column[Integer] = Column(Integer, nullable=False)
    school_class: Column[String] = Column(String(4), nullable=False)
    q_text: Column[String] = Column(String(250))
    files: Column[String] = Column(String(250))
    q_right_answer: Column[String] = Column(String(50), nullable=False)

    def __str__(self): pass

    def __repr__(self): pass

    def get_question(self): pass
