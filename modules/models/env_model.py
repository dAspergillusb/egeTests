from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime
import dotenv
from os.path import exists
from _io import TextIOWrapper


class EnvSettings(BaseSettings):
    INITIATED_DBS: bool = False
    MAIN_DB_USERS_NAME: str = "users_main"
    MAIN_DB_ARCHIVE_NAME: str = "archive_databases"
    MAIN_DB_INFORMATICS_NAME: str = "informatics_main"
    ARCHIVE_DB_NAME: str = "archive_databases"
    INFORMATICS_DB_NAME: str = "informatics_main"
    USERS_DB_NAME: str = "users"
    USERS_STATISTICS_DB_NAME: str = "users_statistics"
    DAILY_STATISTICS_DB_NAME: str = "daily_statistics"
    ACTIVE_STUDENTS_TEST_DB_NAME: str = "active_students_test"
    USERS_SESSIONS_DB_NAME: str = "users_sessions"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = "1440"

    if not exists(".env"):
        print(".env file does not exist, generating default .env...")
        db_user: str = input("What is your postgres superuser name (default: postgres): ")
        db_password: str = input("What is your postgres superuser password (default: postgres): ")
        secret_key: str = input("What is your secret key to jwt-token (default: super-secret-key): ")
        expire_minutes: str = input("How many minutes do you want jwt-token to be valid (default: 1 day): ")
        settings: list[str] = [
            "INITIATED_DBS=False\n",
            f"MAIN_DB_USERS_NAME=users_main_{datetime.now().year}\n",
            f"MAIN_DB_ARCHIVE_NAME=archive_main_{datetime.now().year}\n",
            f"MAIN_DB_INFORMATICS_NAME=informatics_main_{datetime.now().year}\n",
            f"ARCHIVE_DB_NAME=archive_databases_{datetime.now().year}\n",
            f"INFORMATICS_DB_NAME=informatics_{datetime.now().year}\n",
            f"USERS_DB_NAME=users_{datetime.now().year}\n",
            f"USERS_STATISTICS_DB_NAME=users_statistics_{datetime.now().year}\n",
            f"DAILY_STATISTICS_DB_NAME=daily_statistics_{datetime.now().year}\n",
            f"ACTIVE_STUDENTS_TEST_DB_NAME=active_students_test_{datetime.now().year}\n",
            f"USERS_SESSIONS_DB_NAME=users_sessions_{datetime.now().year}\n",
            "DB_HOST=localhost\n",
            "DB_PORT=5432\n",
            f"DB_USER={db_user if db_user else 'postgres'}\n",
            f"DB_PASSWORD={db_password if db_password else 'postgres'}\n",
            f"SECRET_KEY={secret_key if secret_key else 'super-secret-key'}\n",
            "ALGORITHM=HS256\n",
            "ACCESS_TOKEN_EXPIRE_MINUTES=1440"
        ]
        with open(f".env", "w") as env:
            env.writelines(settings)

    model_config = SettingsConfigDict(
        env_file=".env",
        ignored_types=(TextIOWrapper,),
        env_file_encoding="utf-8"
    )

    def __getattr__(self, name: str):
        if name in self.get_main_databases_names():
            return name
        raise AttributeError(f"'{self.__class__.__name__}' объект не имеет атрибута '{name}'")

    def get_databases_names(self) -> dict[str, str]:
        return {
            key: value
            for key, value
            in self.__dict__.items()
            if key.endswith("NAME")
        }

    def get_main_databases_names(self) -> set[str]:
        return {key for key in self.__dict__.keys() if key.startswith("MAIN")}