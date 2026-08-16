from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from asyncpg import connect, DuplicateDatabaseError, ObjectInUseError
from ..endpoints.config import DB_USER, DB_PASSWORD
from ..errors.db_errors import NotMainDBNameError

BASE_USERS = declarative_base()
BASE_INF = declarative_base()
BASE_ARCHIVE = declarative_base()


class MainDB:

    def __init__(self, db_name: str | None):
        if db_name is None:
            raise NotMainDBNameError()
        self.db_name = db_name

    async def create_main_db(self):
        connection = await connect(
            host="localhost",
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        try:
            await connection.execute(f"CREATE DATABASE {self.db_name}")
            print(f"Database {self.db_name} successfully created")
        except DuplicateDatabaseError:
            await connection.execute(f"DROP DATABASE {self.db_name}")
            await connection.execute(f"CREATE DATABASE {self.db_name}")
            print(f"Database {self.db_name} successfully REcreated")
        except ObjectInUseError:
            print(f"Database {self.db_name} is already in use! You need first close all other connections.")

        await connection.close()

    async def close_connections_to_main_db(self):
        connection = await connect(
            host="localhost",
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        disconnect_query = f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{self.db_name}'
                  AND pid <> pg_backend_pid();
            """
        try:
            await connection.execute(disconnect_query)
            print(f"Connections to database {self.db_name} successfully closed")
        except ObjectInUseError:
            print(f"Connection to database {self.db_name} was already closed")

