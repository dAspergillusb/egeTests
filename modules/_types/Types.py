from abc import ABC, abstractmethod
from fastapi import HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session


# BASE = declarative_base()
#
#
# class DataBase(ABC):
#     session: Session
#
#     @abstractmethod
#     def __init__(self): pass
#
#     @abstractmethod
#     def _create_engine(self): pass
#
#     @abstractmethod
#     def _connect(self): pass
#
#     @abstractmethod
#     def add_question(self, *, question_data: dict[str, Column[String] | Column[Integer] | str | int]) -> None: pass
#
#     @abstractmethod
#     def change_question(self, *, question_id: str, data: dict[str, str | int]) -> None: pass
#
#
# class BaseTable(BASE):
#
#     __tablename__ = "base_table"
#     id: Column[Integer] = Column(Integer, primary_key=True)
#     q_number: Column[Integer] = Column(Integer, nullable=False)
#     school_class: Column[String] = Column(String(4), nullable=False)
#     q_text: Column[String] = Column(String(250))
#     files: Column[String] = Column(String(250))
#     q_right_answer: Column[String] = Column(String(50), nullable=False)
#
#     def __str__(self): pass
#
#     def __repr__(self): pass
#
#     def get_question(self): pass


class Ranks:
    STUDENT: str = "student"
    TEACHER: str = "teacher"
    ADMIN: str = "admin"

    def __str__(self):
        return f"Ranks({self.STUDENT=}, {self.TEACHER=}, {self.ADMIN=})"

    def redirect(self, rank: str) -> str:
        conditions: dict[str, str] = {
            self.STUDENT: "/prepare_test",
            self.TEACHER: "/teacher_cabinet",
            self.ADMIN: "/admin_cabinet"
        }
        try:
            return conditions[rank]
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail=f"База данных пользователей повреждена. Пожалуйста, обратитесь к администратору."
            )


class Actions:
    ADD: str = "add"
    REWRITE:str = "rewrite"
    RESTORE: str = "restore"


class HistoryTypes:
    USERS: str = "users"
    INFORMATICS: str = "informatics"

    def __contains__(self, _type: str) -> bool:
        return _type in {self.USERS, self.INFORMATICS}

if __name__ == '__main__':
    print("users" in HistoryTypes())