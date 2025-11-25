from modules.databases.InformaticsDB import Informatics, InformaticsDB


informatics = InformaticsDB().session.query(Informatics).all()

for item in informatics:
    print(item)