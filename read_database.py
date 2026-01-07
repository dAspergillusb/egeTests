from sqlalchemy import Column, Integer
from modules.databases.InformaticsDB import Informatics, InformaticsDB
from modules.databases.UsersDB import Users, UsersDB
from modules.functions.security import generate_code_from_password

"""db = InformaticsDB()
question: Informatics = db.session.query(Informatics).get(3)
question.q_files = "files//3//3_1.xlsx"
db.session.commit()"""


informatics = InformaticsDB().session.query(Informatics).all()
users = UsersDB().session.query(Users).all()

# for item in informatics:
#     print(
#         item.q_number,
#         #item.q_text,
#         item.q_difficulty,
#         item.q_files,
#         item.q_right_answer,
#         sep="\n"
#     )

# UsersDB().change_instance(user_id=1, password=generate_code_from_password("(test#user)"))

print(users[0].password)
