from pydantic import BaseModel


class TestResultData(BaseModel):
    q_1: list[str] = []
    q_2: list[str] = []
    q_3: list[str] = []
    q_4: list[str] = []
    q_5: list[str] = []
    q_6: list[str] = []
    q_7: list[str] = []
    q_8: list[str] = []
    q_9: list[str] = []
    q_10: list[str] = []
    q_11: list[str] = []
    q_12: list[str] = []
    q_13: list[str] = []
    q_14: list[str] = []
    q_15: list[str] = []
    q_16: list[str] = []
    q_17: list[str] = []
    q_18: list[str] = []
    q_19: list[str] = []
    q_20: list[str] = []
    q_21: list[str] = []
    q_22: list[str] = []
    q_23: list[str] = []
    q_24: list[str] = []
    q_25: list[str] = []
    q_26: list[str] = []
    q_27: list[str] = []
    q_28: list[str] = []
    q_29: list[str] = []
    q_30: list[str] = []

    def to_dict(self) -> dict[str, list[str]]:
        return {
            attr[2:]: getattr(self, attr) for attr in self.__dict__
        }