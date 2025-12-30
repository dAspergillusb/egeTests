from typing import Type
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


BASE = declarative_base()


class Users(BASE):
    __tablename__ = "users"
    user_id: Column[Integer] = Column(Integer, primary_key=True)
    firstname: Column[String] = Column(String(100), nullable=False)
    lastname: Column[String] = Column(String(100), nullable=False)
    sex: Column[String] = Column(String(8), nullable=False)
    school_class: Column[String] = Column(String(100))
    subject: Column[String] = Column(String(20), default=None)
    username: Column[String] = Column(String(100), nullable=False)
    password: Column[String] = Column(String(250), nullable=False)
    rank: Column[String] = Column(String(15), default="student")
    active: Column[Boolean] = Column(Boolean, default=True)

    def __contains__(self, item: str):
        return self.username == item

    def __str__(self):
        return f"User: {self.user_id=}, {self.username}"

    def __repr__(self):
        return f"(( User: {self.user_id=}, {self.username} , {self.subject})) "


class UsersDB:

    def __init__(self, db_name: str = "users_db", database_path: str = "database"):
        self.db_name = db_name
        self.database_path = database_path
        self.engine = self._create_engine()
        BASE.metadata.create_all(self.engine)
        BASE.metadata.bind = self.engine
        self.db_session: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.session: Session = self.db_session()

    def _create_engine(self) -> Engine:
        db: Engine = create_engine(f"sqlite:///{self.database_path}/{self.db_name}.db")
        return db

    def _connect(self) -> Connection:
        db_connect: Connection = self.engine.connect()
        return db_connect

    def exist_username(self, username: str | Column[String]) -> bool:
        return bool(self.session.query(Users).filter(Users.username == username).first())

    def exist_email(self, email: str | Column[String]) -> bool:
        return bool(self.session.query(Users).filter(Users.email == email).first())

    def add_instance(self, *, user_data: dict[str, str | int | list[str]]) -> bool | None:
        subject: list[str] = user_data.get("subject")
        user = Users(
            firstname=user_data.get("firstname"),
            lastname=user_data.get("lastname"),
            sex=user_data.get("sex"),
            school_class=user_data.get("school_class"),
            username=user_data.get("username"),
            password=user_data.get("password"),
            rank=user_data.get("rank"),
            subject="&".join(subject) if subject else None
        )

        self.session.add(user)
        self.session.commit()
        return True

    def change_instance(self, user_id: int = None, username: Column[String] = None, *, school_class: str = None, email: str = None,
                        password: str = None, subject: str = None, rank: str = None, active: bool = None) -> bool | None:
        if user_id:
            user: Type[Users] = self.session.query(Users).get(user_id)
        elif username:
            user: Type[Users] = [_user for _user in self.session.query(Users).all() if _user.username == username][0]
        else:
            return False

        if school_class:
            user.school_class = school_class

        if email:
            user.email = email

        if password:
            user.password = password

        if subject:
            if isinstance(subject, list):
                user.subject = "&".join(subject)
            elif isinstance(subject, str):
                user.subject = subject

        if rank:
            user.rank = rank

        if active:
            user.active = active
        self.session.commit()

    def delete_instance(self, _user: Users = None, user_id: Column[Integer] | int = None, username: str = None) -> None:
        if _user:
            self.session.delete(_user)
            self.session.commit()
        elif user_id:
            _user = self.session.query(Users).get(user_id)
            if _user:
                self.session.delete(_user)
                self.session.commit()
        elif username:
            _user: Type[Users] | None = None
            for user in self.session.query(Users).all():
                if user.username == username:
                    _user = user
                    break
            if _user:
                self.session.delete(_user)
                self.session.commit()


if __name__ == '__main__':
    database = UsersDB(database_path="../../../database")
    """database.add_instance(
        firstname="Nik",
        lastname="Zel",
        sex="Male",
        email="pool",
        school_class="10-A",
        username="useradminadmin",
        password="Useradmin1234$"
    )"""
    #database.delete_instance(user_id=23)
    #database.change_instance(user_id=22, subject="английский язык")

    for some_user in database.session.query(Users).all():
        print(f"{some_user.user_id=}::{some_user.username=}::{some_user.firstname=}::{some_user.lastname=}::{some_user.rank=}::{some_user.sex=}::{some_user.password=}::{some_user.school_class=}::{some_user.subject=}::{some_user.email=}")


