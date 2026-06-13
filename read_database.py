from sqlalchemy import Column, Integer
from pprint import pprint
from modules.databases.InformaticsDB import Informatics, InformaticsDB
from modules.databases.UsersStatisticsDB import UsersStatistics, UsersStatisticsDB
from modules.databases.DailyStatisticsDB import DailyStatistics, DailyStatisticsDB
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


informatics = InformaticsDB()
users = UsersDB().session
statistics = UsersStatisticsDB().session
daily = DailyStatisticsDB().session

# for item in informatics:
#     print(
#         item.q_number,
#         #item.q_text,
#         item.q_difficulty,
#         item.q_files,
#         item.q_right_answer,
#         sep="\n"
#     )
# pprint([i for i in informatics.session.query(Informatics).all() if i.id == 16][0].q_text)
pprint([i for i in daily.query(DailyStatistics).all()])
# pprint([i for i in daily.query(DailyStatistics).all() if i.user_id == 1])
# UsersDB().change_instance(user_id=1, password=generate_code_from_password("(test#user)"))
# print(informatics.get(130).q_text)
# for _id in 133, 134, 135, 136:
#     i = informatics.session.query(Informatics).get(_id).q_right_answer
#     informatics.session.query(Informatics).get(_id).q_right_answer = i.replace(" ", "")
# informatics.get(134).q_right_answer = 16
# informatics.get(135).q_right_answer = 16
# informatics.get(136).q_right_answer = 16
# informatics.get(7).q_number = 2
# informatics_ = informatics.session.query(Informatics).all()[-1]
# informatics.session.delete(informatics_)
# informatics.session.commit()
# pprint(users.query(Users).all())
# pprint(statistics.get(UsersStatistics, 1).to_dict())
# pprint(users.query(Users).all())
# pprint(statistics)
# pprint(statistics.query(UsersStatistics).all())
# pprint(daily.query(DailyStatistics).all())
# q = informatics.get(233)
# print(q)
# questions = [q for q in informatics.query(Informatics).all() if q.q_right_answer[-1] == "&"]
#
# for q in questions:
#     while q.q_right_answer[-1] == "&":
#         q.q_right_answer = q.q_right_answer[:-1]
# informatics.commit()
# pprint([str(q) for q in InformaticsDB().session.query(Informatics).all() if q.q_number in [26, 27]])
# student = users.get(Users, 34)
# student.username = "starostine"
# users.commit()
