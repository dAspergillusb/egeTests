from os import mkdir, path, listdir, remove
from pathlib import Path
from typing import Callable
from uuid import uuid4
from aiofiles import open as async_open
from fastapi import UploadFile
from ..functions.security import generate_code_from_password
from anyio import to_thread
from .._types.Types import Ranks, Actions


async def save_to_file(q_number: int, file: UploadFile) -> str:
    filepath: str = f"files/{q_number}/"
    filename_extension: str = Path(file.filename).suffix.lower()
    if not await to_thread.run_sync(path.exists, filepath):
        await to_thread.run_sync(mkdir, filepath)
    # files_value: int = len(listdir(f"files/{q_number}"))
    uuid_name: str = uuid4().hex
    full_filename_filepath: str = f"{filepath}{uuid_name}{filename_extension}"
    async with async_open(full_filename_filepath, "wb") as data:
        await data.write(file.file.read())
    return full_filename_filepath


async def change_file_in_database(database_filepath: str, new_file: UploadFile, q_number: int) -> str:
    new_filepath: str = await save_to_file(q_number=int(q_number), file=new_file)
    await remove_file(database_filepath)
    return new_filepath


async def remove_file(database_filepath: str) -> None:
    if database_filepath:
        try:
            await to_thread.run_sync(remove, database_filepath)
        except FileNotFoundError:
            print(f"There is no file '{database_filepath}' in database! Continue...")
        except TypeError:
            print("Adding new file to database...")


async def change_env_parameter(
        var_name: str,
        old_value: str = "False",
        new_value: str = "True"
) -> None:
    if any((not old_value, not new_value)):
        return
    async with async_open(f".env", "r") as file:
        data: str = await file.read()
    data = data.replace(f"{var_name}={old_value}", f"{var_name}={new_value}")
    # print(var_name, old_value, new_value)
    async with async_open(f".env", "w") as file:
        await file.write(data)


async def env_full_rewrite(full_env: dict[str, str]) -> None:
    env_parameters: str = '\n'.join(
        f"{key}={value}" for key, value in full_env.items()
    )
    async with async_open(f".env", "w") as file:
        await file.write(env_parameters)


if __name__ == '__main__':
    print(uuid4(), uuid8())