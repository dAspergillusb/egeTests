from pydantic import BaseModel
from fastapi import UploadFile, File


class TestCreation(BaseModel):
    q_number: str = ""
    q_text: str = ""
    file_one: UploadFile = None #File(...)
    file_two: UploadFile = None #File(...)
    file_three: UploadFile = None #File(...)
    file_four: UploadFile = None #File(...)
    q_right_answer: str = ""
    q_right_answer_1: str = ""
    q_right_answer_2: str = ""
    q_right_answer_3: str = ""
    q_right_answer_4: str = ""
    q_right_answer_5: str = ""
    q_right_answer_6: str = ""
    q_right_answer_7: str = ""
    q_right_answer_8: str = ""
    q_right_answer_9: str = ""
    q_right_answer_10: str = ""
    q_right_answer_11: str = ""
    q_right_answer_12: str = ""
    q_right_answer_13: str = ""
    q_right_answer_14: str = ""
    q_right_answer_15: str = ""
    q_right_answer_16: str = ""
    q_right_answer_17: str = ""
    q_right_answer_18: str = ""
    q_difficulty: str = ""

    def get_q_number(self) -> str:
        return self.q_number

    def get_q_text(self) -> str:
        return self.q_text

    def get_q_difficulty(self) -> str:
        return self.q_difficulty

    def get_answers(self) -> str:
        q_one_pair_answers: set[str] = {"17", "18", "20", "26"}
        q_two_pair_answers: set[str] = {"27"}
        q_many_pairs_answers: set[str] = {"25"}
        if all([
            self.q_right_answer,
            self.q_number not in q_one_pair_answers | q_two_pair_answers | q_many_pairs_answers,
        ]):
            return self.q_right_answer
        elif all([
            self.q_right_answer_1,
            self.q_right_answer_2,
            self.q_number in q_one_pair_answers
        ]) or all([
            self.q_right_answer_1,
            self.q_right_answer_2,
            self.q_right_answer_3,
            self.q_right_answer_4,
            self.q_number in q_two_pair_answers
        ]) or all([
            all(self.__dict__.get(f"q_right_answer_{num}") for num in range(1, 11)),
            self.q_number in q_many_pairs_answers
        ]):
            return "&".join([
                self.__dict__.get(f"q_right_answer_{num}") for num in range(1, 11) if self.__dict__.get(f"q_right_answer_{num}")
            ])
        return ""

    def get_files(self) -> list[UploadFile]:
        return [
            file for file in [
                self.file_one,
                self.file_two,
                self.file_three,
                self.file_four
            ] if file
        ]


class ImportCSV(BaseModel):
    inf_db_name: str = "informatics_db"
    u_db_name: str = "users_db"
    u_stat_db_name: str = "users_statistics_db"
    csv_file: UploadFile = File(...)

class TestCreation1921(BaseModel):
    q_text_19: str = ""
    q_text_20: str = ""
    q_text_21: str = ""
    q_right_answer_19: str = ""
    q_right_answer_20_1: str = ""
    q_right_answer_20_2: str = ""
    q_right_answer_21: str = ""
    q_difficulty: str = ""

class DataFromTopic(BaseModel):
    topic: str = ""

    def get_topic_number(self) -> int:
        if self.topic:
            return int(self.topic)
        return 0

class QuestionTypeNeeded(BaseModel):
    q_type: str = ""

    def get_q_type(self) -> int:
        if self.q_type:
            return int(self.q_type)
        return 0