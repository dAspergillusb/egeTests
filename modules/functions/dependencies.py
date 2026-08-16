from fastapi import HTTPException, Security, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from ..databases.UsersDB import UsersDB, Users
from ..functions.security import create_access_token
from sqlalchemy.ext.asyncio import session

from .._types.Types import Ranks
from ..databases.UserSessionsDB import UserSessionsDB, UserSessions
from ..endpoints.config import SECRET_KEY, ALGORITHM, SECURED, env_settings


SECURITY: HTTPBearer = HTTPBearer()


class Roles:

    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, response: Response) -> str:
        cookie_token: str = request.cookies.get("access_token", "")

        if not cookie_token or not cookie_token.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Вы не авторизованы. Пожалуйста, войдите в систему."
            )

        token = cookie_token.split()[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_rank: str = payload.get("rank")
            username: str = payload.get("sub")
            session_id: str = payload.get("session_id")

            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидный токен авторизации"
                )
            active_session: type[UserSessions] | None = await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).get_session(session_id=session_id)
            if active_session is None:
                user_id: int = int(request.cookies.get("user_id", 0))
                user_agent: str = request.headers.get("User-Agent", "")
                if not user_id or not user_agent:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Данная сессия завершена. Авторизируйтесь заново."
                    )
                new_session_id: str = await UserSessionsDB(db_name=env_settings.MAIN_DB_USERS_NAME).create_new_session(
                    user_id=user_id,
                    user_agent=user_agent,
                    ip_address=request.client.host,
                )
                response.delete_cookie(
                    key="session_id",
                    httponly=True,
                    secure=SECURED,
                    samesite="lax"
                )
                response.set_cookie(
                    key="session_id",
                    value=new_session_id,
                    httponly=True,
                    secure=SECURED,
                    samesite="lax"
                )
                new_access_token: str = create_access_token(
                    data={
                        "sub": username,
                        "rank": user_rank,
                        "session_id": new_session_id
                    })
                response.set_cookie(
                    key="access_token",
                    value=f"Bearer {new_access_token}",
                    httponly=True,
                    secure=SECURED,
                    samesite="lax"
                )
                return username

        except jwt.ExpiredSignatureError:
            username: str = ""
            user_id: int = int(request.cookies.get("user_id", 0))
            user: type[Users] | None = await UsersDB(db_name=env_settings.MAIN_DB_USERS_NAME).choose_user(user_id=user_id)
            if user: username: str = user.username
            user_rank: str = request.cookies.get("rank", "")
            session_id: str = request.cookies.get("session_id", "")
            if any((
                not username,
                not user_rank,
                not session_id
            )):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Токен устарел. Авторизируйтесь заново."
                )
            new_access_token: str = create_access_token(
                data={
                    "sub": username,
                    "rank": user_rank,
                    "session_id": session_id
                }
            )
            response.set_cookie(
                key="access_token",
                value=f"Bearer {new_access_token}",
                httponly=True,
                secure=SECURED,
                samesite="lax"
            )
            return username
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен повреждён. Авторизируйтесь заново."
            )

        if user_rank not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав! Требуется роль администратора."
            )
        return username
