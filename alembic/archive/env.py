from alembic.common import run_migrations
from modules.endpoints.config import DB_URL_PART, env_settings
from modules.databases.MainDB import BASE_ARCHIVE
import modules.databases.ArchiveDatabasesDB  # noqa: F401

run_migrations(
    f"{DB_URL_PART}{env_settings.MAIN_DB_ARCHIVE_NAME}",
    BASE_ARCHIVE.metadata,
)
