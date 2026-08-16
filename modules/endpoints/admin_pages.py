from typing import BinaryIO, Callable, Any
from fastapi import FastAPI, HTTPException, Form, APIRouter, Depends, UploadFile
from sqlalchemy import Sequence
from starlette import status
from starlette.requests import Request
from starlette.templating import _TemplateResponse
from .._types.Types import Ranks, Actions, HistoryTypes
from ..databases.ActiveStudentsTest import ActiveStudentsTest, ActiveStudentsTestDB
from ..databases.ArchiveDatabasesDB import ArchiveDatabases, ArchiveDatabasesDB
from ..databases.UserSessionsDB import UserSessionsDB, UserSessions
from ..functions.database_operations import (
    create_new_users,
    rewrite_add_table,
    clear_or_create_database_informatics,
    clear_or_create_database_users,
    add_to_archive,
    change_users_parameters,
    change_informatics_parameters
)
from ..functions.files_operations import change_env_parameter
from ..models.admin_models import UsersData, DbData, NewDBName, DatabaseStructure
from ..databases.UsersDB import Users, UsersDB
from ..functions.security import generate_code_from_password
from .main_pages import TEMPLATES
from .config import TOPICS_FOR_ADMIN_CABINET, env_settings
from ..functions.dependencies import Roles
from ..models.test_creation_model import ImportCSV

admin_allowed: Roles = Roles(allowed_roles=[Ranks.ADMIN])

def register_admin_pages(app: FastAPI):

    @app.get("/admin_cabinet")
    def get_admin_cabinet(
            request: Request,
            name: str = Depends(admin_allowed)
    ) -> _TemplateResponse:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="/admin_cabinet.html",
            context={
                "request": request,
                "name": name,
                "topics": enumerate(TOPICS_FOR_ADMIN_CABINET, start=1),
                "nav_topic": "Кабинет администратора"
            }
        )

    @app.get("/users")
    async def get_all_users(
            request: Request,
            _ = Depends(admin_allowed)
    ):
        users: Sequence[Users] = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_all_users()
        return sorted(users, key=lambda user: user.rank)

    @app.get("/users/{user_id}")
    async def get_user(
            request: Request,
            user_id: int,
            _ = Depends(admin_allowed)
    ):
        user: type[Users] | None = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).choose_user(user_id=user_id)
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")

    @app.patch("/users/{user_id}")
    async def change_user_data(
            request: Request,
            user_id: int,
            user_data: UsersData,
            _ = Depends(admin_allowed)
    ):
        success_change: bool = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).change_user_data(
            data_to_change=user_data.__dict__,
            user_id=user_id
        )
        return success_change

    @app.post("/users")
    async def create_user(
        request: Request,
        user_data: UsersData,
        _ = Depends(admin_allowed)
    ):
        if any((
            all((user_data.rank == Ranks.STUDENT, user_data.full_create_student())),
            all((user_data.rank in {Ranks.ADMIN, Ranks.TEACHER}, user_data.full_create_teacher_admin()))
        )):
            user_data.password = generate_code_from_password(user_data.password)
            user: bool | int | Users = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).add_user(user_data.__dict__)
            return user
        return False

    @app.delete("/users/{user_id}")
    async def delete_user(
            request: Request,
            user_id: int,
            _ = Depends(admin_allowed)
    ):
        deleted: bool | int = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).delete_user(user_id)
        if deleted:
            return True
        return deleted

    @app.get('/databases')
    async def get_databases_names(
            request: Request,
            _ = Depends(admin_allowed)
    ):
        return env_settings.get_databases_names()

    @app.get("/databases/active_users_sessions")
    async def get_active_users_sessions(
            request: Request,
            _ = Depends(admin_allowed)
    ):
        current_session_id: str = request.cookies.get("session_id", "")
        if not current_session_id:
            return status.HTTP_404_NOT_FOUND
        active_sessions = await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_active_sessions(
            current_session_id=current_session_id
        )
        return active_sessions

    @app.delete('/database/active_users_sessions/{session_id}')
    async def delete_expired_session(
            request: Request,
            session_id: str,
            _ = Depends(admin_allowed)
    ):
        await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).delete_session(session_id=session_id)
        return status.HTTP_200_OK

    @app.post('/databases/table/{action}')
    async def rewrite_or_add_table(
            request: Request,
            action: str,
            db_data: DbData = Form(...),
            _ = Depends(admin_allowed)
    ):
        file: UploadFile = db_data.csv_file
        if file.content_type and file.content_type.endswith("csv"):
            file_data: BinaryIO = db_data.csv_file.file
            file_data.readline()
        else:
            return {
                "status": status.HTTP_409_CONFLICT,
                "message": "Неправильный формат файла! Должно быть csv-расширение."
            }
        try:
            await rewrite_add_table(
                action=action,
                csv_file=file_data.read().decode("utf-8")
            )
        except UnicodeDecodeError:
            return {
                "status": status.HTTP_409_CONFLICT,
                "message": "Неправильный формат csv-файла! Проверьте кодировку файла. Должна быть utf-8."
            }
        except ValueError:
            return {
                "status": status.HTTP_409_CONFLICT,
                "message": "Неправильный формат csv-файла! Проверьте правильность заполнения строк."
            }
        return {
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Успешная операция с базами данных."
        }

    @app.put("/databases/clear/{db_type}")
    async def clear_database(
            request: Request,
            db_type: str,
            _ = Depends(admin_allowed)
    ):
        is_correct_db_type: Callable | None = {
            HistoryTypes.INFORMATICS: clear_or_create_database_informatics,
            HistoryTypes.USERS: clear_or_create_database_users
        }.get(db_type)
        if is_correct_db_type:
            return await is_correct_db_type(request=request)
        return status.HTTP_404_NOT_FOUND

    @app.post("/databases/create/{db_type}")
    async def create_database(
            request: Request,
            db_type: str,
            new_db_name: NewDBName,
            _ = Depends(admin_allowed)
    ):
        print(new_db_name, db_type)
        possible_types: dict[str, dict[str, Callable | str]] = {
            HistoryTypes.INFORMATICS: {
                "name": "MAIN_DB_INFORMATICS_NAME",
                "func": clear_or_create_database_informatics
            },
            HistoryTypes.USERS: {
                "name": "MAIN_DB_USERS_NAME",
                "func": clear_or_create_database_users
            }
        }
        if db_type in possible_types:
            old_db_name: str = getattr(env_settings, possible_types[db_type]["name"])
            # setattr(env_settings, possible_types[db_type]["name"], new_db_name.database_name)
            await possible_types[db_type]["func"](
                request=request,
                db_type=possible_types[db_type]["name"],
                new_db_name=new_db_name.database_name
            )
            await add_to_archive(db_type=db_type)
            await change_env_parameter(
                var_name=possible_types[db_type]["name"],
                old_value=old_db_name,
                new_value=new_db_name.database_name
            )
            return status.HTTP_201_CREATED
        return status.HTTP_404_NOT_FOUND


    @app.get("/databases/active_tests_sessions")
    async def get_active_tests_sessions(
            request: Request,
            _ = Depends(admin_allowed)
    ):
        active_test_sessions: list[dict[str, str]] = await ActiveStudentsTestDB(
            db_name=env_settings.MAIN_DB_USERS_NAME
        ).get_all_test_sessions(join=Users)
        if active_test_sessions:
            return active_test_sessions
        return status.HTTP_404_NOT_FOUND


    @app.delete("/databases/active_tests_sessions/{ast_id}")
    async def delete_active_test_session(
            request: Request,
            ast_id: int,
            _ = Depends(admin_allowed)
    ):
        _session: ActiveStudentsTestDB = ActiveStudentsTestDB(db_name=env_settings.MAIN_DB_USERS_NAME)
        active_test_session: type[ActiveStudentsTest] | None = await _session.get_test_session(ast_id=ast_id)
        if active_test_session:
            await _session.remove_test_session(ast_id=ast_id)
            return status.HTTP_204_NO_CONTENT
        return status.HTTP_404_NOT_FOUND


    @app.get("/databases/archived")
    async def get_archived_databases(
            request: Request,
            _ = Depends(admin_allowed)
    ):
        archives: dict[str, str | list[dict[str, str]]] = await ArchiveDatabasesDB(
            db_name=env_settings.MAIN_DB_ARCHIVE_NAME
        ).get_all_history()
        archives["active_u_db"] = env_settings.MAIN_DB_USERS_NAME
        archives["active_i_db"] = env_settings.MAIN_DB_INFORMATICS_NAME
        print(archives)
        return archives


    @app.post("/databases/archives")
    async def activate_main_db(
            request: Request,
            chosen_database: DatabaseStructure,
            _ = Depends(admin_allowed)
    ):
        print(chosen_database.__dict__)
        change_env_parameters: dict[str, tuple[Callable, dict[str, str | Request]]] = {
            HistoryTypes.USERS: (
                change_users_parameters,
                {
                    'db_structure': chosen_database.db_structure,
                    'request': request
                }
            ),
            HistoryTypes.INFORMATICS: (
                change_informatics_parameters,
                {'db_structure': chosen_database.db_structure}
            )
        }
        if chosen_database.db_type in change_env_parameters:
            db_type: str = chosen_database.db_type
            func, kwargs = change_env_parameters[db_type][0], change_env_parameters[db_type][1]
            return await func(**kwargs)
        return status.HTTP_404_NOT_FOUND



    # @app.get("/import_from_csv")
    # def get_page_import_from_csv(request: Request) -> _TemplateResponse:
    #     return TEMPLATES.TemplateResponse(
    #         request=request,
    #         name="import_from_csv.html",
    #         context={
    #             "request": request,
    #             "mistake": "not",
    #             "nav_topic": "Создание базы данных"
    #         }
    #     )

    @app.post("/import_from_csv")
    async def post_import_from_csv(
            request: Request,
            data_to_load: ImportCSV = Form(default=""),
            _=Depends(admin_allowed)
    ) -> _TemplateResponse:
        # print(data_to_load)
        csv_file: str = data_to_load.csv_file.file.read().decode("utf-8")
        print(csv_file)
        new_users: bool = await create_new_users(csv_file=csv_file)
        mistakes: dict[bool, str] = {
            new_users: "Новые пользователи успешно добавлены в базу",
            not new_users: "В csv-файле есть ошибки. Пользователи не добавлены!"
        }
        # print([item for item in reader(data_to_load.csv_file.file.read().decode("utf-8"), delimiter=";")])
        return TEMPLATES.TemplateResponse(
            request=request,
            name="import_from_csv.html",
            context={
                "request": request,
                "mistake": not new_users,
                "mistake_text": mistakes[True],
                "nav_topic": "Создание базы данных"
            }
        )

    @app.get("/to_html_tags")
    def get_page_to_html_tags(
            request: Request,
            firstname: str,
            lastname: str
    ) -> _TemplateResponse:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="to_html_tags.html",
            context={
                "request": request,
                "firstname": firstname,
                "lastname": lastname,
                "nav_topic": "Получить ckeditor-данные из текста"
            }
        )

    @app.post("/to_html_tags")
    async def post_to_html_tags(request: Request, html_tags: str):
        print(html_tags)
        return {"html_tags": html_tags}