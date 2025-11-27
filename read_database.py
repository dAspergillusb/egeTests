from sqlalchemy import Column, Integer
from modules.databases.InformaticsDB import Informatics, InformaticsDB

"""db = InformaticsDB()
question: Informatics = db.session.query(Informatics).get(3)
question.q_files = "files//3//3_1.xlsx"
db.session.commit()"""


informatics = InformaticsDB().session.query(Informatics).all()

for item in informatics:
    if item.q_number == 3:
        print(
            item.q_number,
            #item.q_text,
            item.q_files,
            item.q_right_answer,
            sep="\n"
        )
