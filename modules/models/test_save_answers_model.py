from pydantic import BaseModel


class AnswerForSave(BaseModel):
    q_num: str = ""
    answer: list[str] = []

    def is_empty(self) -> bool:
        return "".join(self.answer) == ""

class AnswerForCheck(BaseModel):
    q_from_old_test: str = ""
    answer: list[str] = []

    def is_empty(self) -> bool:
        return "".join(self.answer) == ""