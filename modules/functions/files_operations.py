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
            "firstname": user[0],
            "lastname": user[1],
            "sex": user[2],
            "school_class": user[3],
            "username": user[4],
            "password": generate_code_from_password(user[5])
        } for user in [line.split(";") for line in csv_file]
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
                "school_class": user_data["school_class"],
                "q_type_1": "0&0&0",
                "q_type_2": "0&0&0",
                "q_type_3": "0&0&0",
                "q_type_4": "0&0&0",
                "q_type_5": "0&0&0",
                "q_type_6": "0&0&0",
                "q_type_7": "0&0&0",
                "q_type_8": "0&0&0",
                "q_type_9": "0&0&0",
                "q_type_10": "0&0&0",
                "q_type_11": "0&0&0",
                "q_type_12": "0&0&0",
                "q_type_13": "0&0&0",
                "q_type_14": "0&0&0",
                "q_type_15": "0&0&0",
                "q_type_16": "0&0&0",
                "q_type_17": "0&0&0",
                "q_type_18": "0&0&0",
                "q_type_19": "0&0&0",
                "q_type_20": "0&0&0",
                "q_type_21": "0&0&0",
                "q_type_22": "0&0&0",
                "q_type_23": "0&0&0",
                "q_type_24": "0&0&0",
                "q_type_25": "0&0&0",
                "q_type_26": "0&0&0",
                "q_type_27": "0&0&0"
            }
        )
        change_db_names(
            u_db_name=u_db_name,
            u_stat_db_name=u_stat_db_name
        )
    return True
