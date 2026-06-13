from pydantic import BaseModel

class ForQuestionData(BaseModel):
    q_num: str = ""

    def get_q_num(self) -> int:
        return int(self.q_num)
