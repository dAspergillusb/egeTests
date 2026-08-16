from typing import Optional
from fastapi import Form, UploadFile, File
from pydantic import BaseModel, Field


class UsersData(BaseModel):
    firstname: str = ""
    lastname: str = ""
    sex: str = ""
    school_class: str = ""
    username: str = ""
    password: str = ""
    rank: str = ""
    active: bool = True

    def full_create_student(self):
        return all((
            getattr(self, attr) for attr in self.__dict__
        ))

    def full_create_teacher_admin(self):
        return all((
            getattr(self, attr) for attr in self.__dict__ if attr != "school_class"
        ))


class DbData(BaseModel):
    main_db_name: Optional[str] = ""
    informatics_db_name: Optional[str] = ""
    users_db_name: Optional[str] = ""
    users_statistics_db_name: Optional[str] = ""
    daily_statistics_db_name: Optional[str] = ""
    csv_file: UploadFile = File(...)


class NewDBName(BaseModel):
    database_name: str = ""


class DatabaseStructure(BaseModel):
    db_type: str = ""
    db_structure: dict[str, str] = dict()


if __name__ == '__main__':
    print(UsersData(
        firstname="firstname",
        lastname="lastname",
        sex="sex",
        school_class="school_class",
        password="password",
        rank="rank",
        active=True
    ).__dict__)

