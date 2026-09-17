from migration_utils import run_migrations
from modules.endpoints.config import DB_URL_PART, env_settings
from modules.databases.MainDB import BASE_INF
import modules.databases.InformaticsDB  # noqa: F401

run_migrations(
    f"{DB_URL_PART}{env_settings.MAIN_DB_INFORMATICS_NAME}",
    BASE_INF.metadata,
)
