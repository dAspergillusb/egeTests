from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    DB_PASSWORD: str = Field(min_length=1)

    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = "1440"
    SECURED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
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
