from datetime import datetime, timedelta, timezone
from string import printable
from random import randint, choice
from typing import Optional, Any
from jwt import encode as jwt_encode
from ..endpoints.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def generate_code_from_password(password: str) -> str:
    encrypted: list[str] = []
    alphabet: str = printable[:72]
    slider: list[str] = list(printable[72:94])
    min_index: int = 0
    max_index: int = len(alphabet) - 1
    for char in password.strip():
        shift: int = randint(min_index, max_index)
        encrypted.append(f"{shift}{alphabet[(alphabet.index(char) + shift) % len(alphabet)]}{choice(slider)}")
    return "".join(encrypted)


def check_password(password: str, password_from_db: str) -> bool:
    slider: list[str] = list(printable[72:94])
    dict_to_clear: dict[str, str] = {char: " " for char in slider}
    alphabet: str = printable[:72]
    if any(char not in alphabet for char in password):
        return False
    password_from_db_cleared: list[str] = password_from_db.translate(str.maketrans(dict_to_clear)).split()
    password_to_check: list[str] = []
    for char, group in zip(password, password_from_db_cleared):
        index: int = 0
        cache: list[str] = []
        while group[index].isdigit() and len(cache) < len(group) - 1:
            cache.append(group[index])
            index += 1
        shift: int = int("".join(cache))
        password_to_check.append(f"{shift}{alphabet[(alphabet.index(char) + shift) % len(alphabet)]}")
    return password_to_check == password_from_db_cleared

def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode: dict[str, Any] = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode["exp"] = expire
    return jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


if __name__ == '__main__':
    # print(printable[:72])
    # print(printable[73:94])
    _password = "755364()()()()(PaSsWoR#d1874281"
    _pass = generate_code_from_password(_password)
    print(_pass)
    check = check_password(_password, _pass)
    print(check)
    print(check_password(password="ПРивет", password_from_db="JKEGFUEW"))
