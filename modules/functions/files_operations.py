from os import mkdir, path, listdir
from fastapi import UploadFile


def save_to_file(q_number: str, file: UploadFile) -> str:
    filename_extension: str = file.filename.split(".")[-1]
    if not path.exists(f"files/{q_number}"):
        mkdir(f"files/{q_number}")
    files_value: int = len(listdir(f"files/{q_number}"))
    with open(f"files/{q_number}/{q_number}_{files_value + 1}.{filename_extension}", "wb") as data:
        data.write(file.file.read())
    return f"files/{q_number}/{q_number}_{files_value + 1}.{filename_extension}"