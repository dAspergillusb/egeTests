from collections.abc import Sequence
from itertools import zip_longest
from typing import Callable
from fastapi import UploadFile, File, HTTPException
from sqlalchemy import (
    select,
    Result,
    Select,
    Integer,
    String,
    or_,
    and_,
    ColumnElement
)
from sqlalchemy.dialects.mssql import information_schema
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    async_sessionmaker
)
from ..endpoints.config import DB_URL_PART, env_settings
from ..functions.files_operations import change_file_in_database, remove_file
from .MainDB import BASE_INF
from ..errors.db_errors import NotMainDBNameError


class Informatics(BASE_INF):
    """
    class base of table for database with questions for Informatics subject.
    """
    __tablename__: str = env_settings.INFORMATICS_DB_NAME
    q_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    q_number: Mapped[int] = mapped_column(Integer, nullable=False)
    q_school_class: Mapped[str] = mapped_column(String, nullable=False)
    q_text: Mapped[str] = mapped_column(String)
    q_difficulty: Mapped[str] = mapped_column(String)
    q_files: Mapped[str] = mapped_column(String, default="")
    q_right_answer: Mapped[str] = mapped_column(String, nullable=False)
    q_linked_with: Mapped[str] = mapped_column(String, default="")

    def __str__(self):
        return f"Informatics(\nq_id={self.q_id},\nnumber={self.q_number},\nclass={self.q_school_class}\n,answer={self.q_right_answer}\n,difficulty={self.q_difficulty})\n"

    def __repr__(self):
        return f"Informatics(\nq_id={self.q_id},\nq_number={self.q_number},\n" + \
                f"school_class={self.q_school_class}\nfiles={self.q_files}\ndifficulty={self.q_difficulty}\nanswers={self.q_right_answer})\n"

    def get_question(self) -> dict[str, Mapped[str] | Mapped[int]]:
        return {
            "q_id": self.q_id,
            "q_number": self.q_number,
            "q_school_class": self.q_school_class,
            "q_text": self.q_text,
            "q_difficulty": self.q_difficulty,
            "q_files": self.q_files,
            "q_right_answer": self.q_right_answer,
            "q_linked_with": self.q_linked_with
        }


class InformaticsDB:
    """
    Class connects to database with questions for tests with Informatics subject. Class can create new question
    in database.
    """
    def __init__(self, db_name: str | None):
        if not db_name:
            raise NotMainDBNameError("There is no main informatics database name (MAIN_DB_INFORMATICS_NAME). Check your .enf-file.")
        self.db_name = db_name
        self.engine = self._create_engine()
        self.session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def _create_engine(self) -> AsyncEngine:
        db: AsyncEngine = create_async_engine(f"{DB_URL_PART}{self.db_name}")
        return db

    async def init_db(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(BASE_INF.metadata.create_all)
            print(f"Database initialized: {Informatics.__tablename__}")

    async def get_question(self, q_id: int) -> type[Informatics] | None:
        async with self.session() as session:
            return await session.get(Informatics, q_id)

    async def get_all_questions(self) -> Sequence[Informatics]:
        async with self.session() as session:
            statement: Select[tuple[Informatics]] = select(Informatics)
            all_questions: Result[tuple[Informatics]] = await session.execute(statement)
            return all_questions.scalars().all()

    async def get_all_typed_questions(self, conditions: tuple[ColumnElement[bool], ...], _or: bool = False) -> list[Informatics]:
        async with self.session() as session:
            if _or:
                statement: Select[tuple[Informatics]] = select(Informatics).where(or_(*conditions))
            else:
                statement: Select[tuple[Informatics]] = select(Informatics).where(and_(*conditions))
            typed_questions: Result[tuple[Informatics]] = await session.execute(statement)
            return list(typed_questions.scalars().all())

    async def add_question(self, *, question_data: dict[str, str | int]) -> int:
        async with self.session() as session:
            question: Informatics = Informatics(**question_data)
            session.add(question)
            await session.commit()
        return question.q_id

    async def change_question(self, *, data: dict[str, Mapped[str] | str | int], files: list[UploadFile] | None = None) -> list[type[Informatics] | None]:
        q_id: int = data.pop("q_id")
        async with self.session() as session:
            question_to_change: type[Informatics] | None = await session.get(Informatics, q_id)
            if question_to_change:
                q_number: int = question_to_change.q_number
                old_questions_files = question_to_change.q_files.split("&")
                if all((old_questions_files, files)):
                    new_filepaths: list[str] = [
                        await change_file_in_database(from_database, to_database, q_number)
                        if to_database.filename else from_database
                        for from_database, to_database in zip_longest(old_questions_files, files, fillvalue=UploadFile(File()))
                    ]
                    data["q_files"] = "&".join(new_filepaths)
                for parameter, value in data.items():
                    setattr(question_to_change, parameter, value)
                await session.commit()
                changed_question: type[Informatics] | None = await session.get(Informatics, q_id)
                return [changed_question]
        return []

    async def change_special_question(self, *, data: dict[int, dict[str, Mapped[str] | str | int]]) -> list[type[Informatics] | None]:
        q_id: int = data.get(19).pop("q_id")
        async with self.session() as session:
            question_nineteen_to_change: type[Informatics] | None = await session.get(Informatics, q_id)
            if question_nineteen_to_change:
                q_id_twenty, q_id_twenty_one = map(int, question_nineteen_to_change.q_linked_with.split("&"))
                question_twenty_to_change: type[Informatics] | None = await session.get(Informatics, q_id_twenty)
                question_twenty_one_to_change: type[Informatics] | None = await session.get(Informatics, q_id_twenty_one)
                for parameter, value in data[19].items():
                    setattr(question_nineteen_to_change, parameter, value)
                for parameter, value in data[20].items():
                    setattr(question_twenty_to_change, parameter, value)
                for parameter, value in data[21].items():
                    setattr(question_twenty_one_to_change, parameter, value)
                await session.commit()

                changed_question_nineteen: type[Informatics] | None = await session.get(Informatics, q_id)
                changed_question_twenty: type[Informatics] | None = await session.get(Informatics, q_id_twenty)
                changed_question_twenty_one: type[Informatics] | None = await session.get(Informatics, q_id_twenty_one)

                return [changed_question_twenty, changed_question_twenty_one, changed_question_nineteen]
        return []

    async def delete_question(self, *, q_id: int) -> bool | HTTPException:
        async with self.session() as session:
            question: type[Informatics] | None = await session.get(Informatics, q_id)
            if question is None:
                raise HTTPException(status_code=404, detail="Question not found")
            is_special_question_number = {
                question.q_number != 19: self._delete_standard_question,
                question.q_number == 19: self._delete_special_question,
            }
            return await is_special_question_number[True](session=session, question=question)

    @staticmethod
    async def _delete_standard_question(session: AsyncSession, question: type[Informatics]) -> bool:
        if question.q_files:
            for filepath in question.q_files.split("&"):
                await remove_file(database_filepath=filepath)
        await session.delete(question)
        await session.commit()
        return True

    @staticmethod
    async def _delete_special_question(session: AsyncSession, question: type[Informatics]) -> bool:
        q_twenty_id, q_twenty_one_id = map(int, question.q_linked_with.split("&"))
        question_twenty: type[Informatics] | None = await session.get(Informatics, q_twenty_id)
        question_twenty_one: type[Informatics] | None = await session.get(Informatics, q_twenty_one_id)
        if any((
            question_twenty is None,
            question_twenty_one is None
        )):
            raise HTTPException(status_code=404, detail="Question not found")
        await session.delete(question)
        await session.delete(question_twenty)
        await session.delete(question_twenty_one)
        await session.commit()
        return True

    async def close_engine(self, db_name: str) -> None:
        await self.engine.dispose()
        del self.engine
        print(f"Pull of engine connection with {db_name} closed.")


if __name__ == '__main__':
    # _question = InformaticsDB()
    # for num in range(100):
    #     _question.add_question(question_data={
    #         "q_number": num,
    #         "q_text": f"Problem_{num}",
    #         "q_school_class": "11Б",
    #         "q_files": "Solute_problem_{num}",
    #         "q_right_answer": "9-Б"
    #     }
    #     )
    print(File().filename)
    """for question_num in range(21):
        print(_question.session.query(Informatics).all()[question_num].question_name)"""
