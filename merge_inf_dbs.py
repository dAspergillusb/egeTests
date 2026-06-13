from modules.databases.InformaticsDB_old import InformaticsDB as InformaticsDBOld
from modules.databases.InformaticsDB_old import Informatics as InformaticsOld
from modules.databases.InformaticsDB import Informatics, InformaticsDB

old_inf_db = InformaticsDBOld(db_name="informatics_db_old").session.query(InformaticsOld).all()
inf_db = InformaticsDB()

for q in old_inf_db:
    if q.q_number == 19:
        continue
    inf_db.add_question(question_data=q.get_question())

inf_db = InformaticsDB().session.query(Informatics).all()
print(inf_db)



