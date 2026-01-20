from sqlalchemy import Column, Integer
from pprint import pprint
from modules.databases.InformaticsDB import Informatics, InformaticsDB
from modules.databases.UsersStatisticsDB import UsersStatistics, UsersStatisticsDB
from modules.databases.UsersDB import Users, UsersDB
from modules.functions.security import generate_code_from_password

"""db = InformaticsDB()
question: Informatics = db.session.query(Informatics).get(3)
question.q_files = "files//3//3_1.xlsx"
db.session.commit()"""

# session = InformaticsDB().session
# to_delete = session.query(Informatics).get(13)
# session.delete(to_delete)
# session.commit()
# session.close()


informatics = InformaticsDB().session.query(Informatics)
users = UsersDB().session.query(Users)
statistics = UsersStatisticsDB().session

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
# informatics.get(13).q_number = 2
# informatics.session.commit()
pprint(users.all())
pprint(statistics.get(UsersStatistics, 1).to_dict())
# pprint(users)
# pprint(statistics)
# pprint(statistics[0].to_dict())
