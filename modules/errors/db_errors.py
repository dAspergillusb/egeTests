

class NotMainDBNameError(Exception):
    def __init__(self, message: str = "") -> None:
        default_message: str = "There is no MAIN_DB_NAME (MAIN_DB_NAME is None)! Check your .env-file."
        super().__init__(message if message else default_message)