from .endpoints.main_pages import register_main_endpoints
from .endpoints.creation_pages import register_creation_pages
from .endpoints.tests_pages import register_tests_pages
from .endpoints.admin_pages import register_admin_pages
from .endpoints.config import (
    INITIATED_DBS,
    env_settings,
    # MAIN_DB_USERS_NAME,
    # MAIN_DB_INFORMATICS_NAME,
    # MAIN_DB_ARCHIVE_NAME
)
from .databases.ArchiveDatabasesDB import ArchiveDatabasesDB
from .databases.ActiveStudentsTest import ActiveStudentsTestDB
from .databases.DailyStatisticsDB import DailyStatisticsDB
from .databases.InformaticsDB import InformaticsDB
from .databases.UsersDB import Users, UsersDB
from .databases.UsersStatisticsDB import UsersStatisticsDB
from .databases.UserSessionsDB import UserSessionsDB
from .functions.files_operations import change_env_parameter
from .functions.database_operations import create_new_users
from .errors.db_errors import NotMainDBNameError
from .databases.MainDB import MainDB
from ._types.Types import HistoryTypes