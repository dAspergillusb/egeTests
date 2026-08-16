from collections import defaultdict
from asyncio import CancelledError
from sqlalchemy import (
    select,
    Result,
    Select,
    Integer,
    String, Sequence
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import OperationalError, IntegrityError, DBAPIError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from ..endpoints.config import DB_URL_PART, env_settings
from .._types.Types import HistoryTypes
from .MainDB import BASE_ARCHIVE
from ..errors.db_errors import NotMainDBNameError


class ArchiveDatabases(BASE_ARCHIVE):
    """
    Class represents archive of databases with tables structures (names of database and names of tables inside)
    Structure of class:
    history_type: 'string with type information' (can be 'users' or 'informatics')
    main_db_name: 'dictionary with name of main database'
    db_structure: 'dictionary with names of database tables'

    It's looks like:
    history_type: 'users'
    main_db_name: {'MAIN_DB_NAME': 'users_main'}
    db_structure: {
        'USERS_DB_NAME': 'users',
        'USERS_STATISTICS_DB_NAME': 'users_statistics',
        'DAILY_STATISTICS_DB_NAME': 'daily_statistics',
        'ACTIVE_STUDENTS_TEST_DB_NAME': 'active_students_test'
    }

    This is the name of the main database and the structure of tables inside it.
    This structure is ready to load into system to EnvSettings-object.
    """
    __tablename__: str = env_settings.ARCHIVE_DB_NAME
    ad_id: Mapped[int] = mapped_column(primary_key=True)
    history_type:Mapped[str] = mapped_column(String)
    main_db_name: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)
    db_structure: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict)


class ArchiveDatabasesDB:

    def __init__(self, db_name: str | None) -> None:
        if not db_name:
            raise NotMainDBNameError
        self.db_name = db_name
        self.engine = self._create_engine()
        self.session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def _create_engine(self) -> AsyncEngine:
        return create_async_engine(f"{DB_URL_PART}{self.db_name}")

    async def init_db(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(BASE_ARCHIVE.metadata.create_all)
            print(f"Database initialized: {ArchiveDatabases.__tablename__}")

    async def get_all_history(self) -> dict[str, list[dict[str, str]]]:
        async with self.session() as session:
            statement: Select[tuple[ArchiveDatabases]] = select(ArchiveDatabases)
            result: Result[tuple[ArchiveDatabases]] = await session.execute(statement)
            archives: Sequence[ArchiveDatabases] = result.scalars().all()
        archives_dict = defaultdict(list)
        for archive in archives:
            archives_dict[archive.history_type].append(archive)
        return archives_dict

    async def get_history_by_id(self, *, ad_id: int) -> type[ArchiveDatabases] | None:
        async with self.session() as session:
            return await session.get(ArchiveDatabases, ad_id)

    async def get_history_by_main_name(self, *, main_db_name: str) -> type[ArchiveDatabases] | None:
        async with self.session() as session:
            statement: Select[tuple[ArchiveDatabases]] = select(ArchiveDatabases).where(ArchiveDatabases.main_db_name == main_db_name)
            result: Result[tuple[ArchiveDatabases]] = await session.execute(statement)
            return result.scalars().first()

    async def add_history(self, *, history_type: str, history_data: dict[str, dict[str, str]]) -> bool:
        main_db_name, db_structure = history_data.get("main_db_name", ""), history_data.get("db_structure", "")
        if all((
            history_type in HistoryTypes(),
            main_db_name,
            all((value for value in db_structure.values()))
        )):
            async with self.session() as session:
                new_history = ArchiveDatabases(
                    history_type=history_type,
                    main_db_name=main_db_name,
                    db_structure=db_structure
                )
                session.add(new_history)
                try:
                    await session.commit()
                except IntegrityError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error.detail}")
                    return False
                except OperationalError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error.detail}")
                    return False
                except DBAPIError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error.detail}")
                    return False
                except CancelledError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error}")
                    return False
                return True
        return False

    async def delete_history(self, *, ad_id: int) -> bool:
        history: type[ArchiveDatabases] | None = await self.get_history_by_id(ad_id=ad_id)
        if history:
            async with self.session() as session:
                try:
                    await session.delete(history)
                except OperationalError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error.detail}")
                    return False
                except DBAPIError as error:
                    await session.rollback()
                    print(f"While executing there is an error: {error.detail}")
                    return False
                return True
        return False
