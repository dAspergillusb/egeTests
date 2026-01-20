from os import mkdir, path, listdir
from fastapi import UploadFile
from ..functions.security import generate_code_from_password
from ..databases.UsersDB import Users, UsersDB
from ..databases.UsersStatisticsDB import UsersStatistics, UsersStatisticsDB
from ..endpoints.config import load_db_names

def save_to_file(q_number: str, file: UploadFile) -> str:
    filename_extension: str = file.filename.split(".")[-1]
    if not path.exists(f"files/{q_number}"):
        mkdir(f"files/{q_number}")
    files_value: int = len(listdir(f"files/{q_number}"))
    with open(f"files/{q_number}/{q_number}_{files_value + 1}.{filename_extension}", "wb") as data:
        data.write(file.file.read())
    return f"files/{q_number}/{q_number}_{files_value + 1}.{filename_extension}"

def change_db_names(
        *,
        u_db_name: str,
        u_stat_db_name: str,
        inf_db_name: str = "informatics_db"
) -> None:
    with open("db_names.txt", "w") as new_db_names:
        new_db_names.write(
            f"{inf_db_name}\n{u_db_name}\n{u_stat_db_name}"
        )
    load_db_names()

def create_new_dbs(
        csv_file: str,
        u_db_name: str,
        u_stat_db_name: str,
        inf_db_name: str = "informatics_db"
) -> bool:
    data_to_load: list[dict[str, str | int]] = [
        {
            "firstname": firstname,
            "lastname": lastname,
            "sex": sex,
            "school_class": school_class,
            "username": username,
            "password": generate_code_from_password(password=password)
        }
        for firstname, lastname, sex, school_class, username, password in [line.split(";") for line in csv_file.split("\n")][:-1]
    ]
    new_u_db: UsersDB = UsersDB(db_name=u_db_name)
    new_u_stat_db: UsersStatisticsDB = UsersStatisticsDB(db_name=u_stat_db_name)
    for user_data in data_to_load:
        new_u_db.add_instance(user_data=user_data)
        new_u_stat_db.add_statistics(
            statistics_data=
            {
                "firstname": user_data["firstname"],
                "lastname": user_data["lastname"],
                "school_class": user_data["school_class"]
            }
        )
    change_db_names(
        u_db_name=u_db_name,
        u_stat_db_name=u_stat_db_name
    )
    return True
