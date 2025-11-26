from pydantic import BaseModel


class TestResultData(BaseModel):
    q_1: str = ""
    q_2: str = ""
    q_3: str = ""
    q_4: str = ""
    q_5: str = ""
    q_6: str = ""
    q_7: str = ""
    q_8: str = ""
    q_9: str = ""
    q_10: str = ""
    q_11: str = ""
    q_12: str = ""
    q_13: str = ""
    q_14: str = ""
    q_15: str = ""
    q_16: str = ""
    q_17: str = ""
    q_18: str = ""
    q_19: str = ""
    q_20: str = ""
    q_21: str = ""
    q_22: str = ""
    q_23: str = ""
    q_24: str = ""
    q_25: str = ""
    q_26: str = ""
    q_27: str = ""

    def to_dict(self):
        return {
            attr[2:]: getattr(self, attr) for attr in self.__dict__
        }