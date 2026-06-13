from modules.databases.UsersDB import UsersDB, Users
from modules.databases.UsersStatisticsDB import UsersStatistics, UsersStatisticsDB

users = UsersDB().session.query(Users)
needed_users = [
    users.get(34),
    users.get(35)
]

users_statistics = UsersStatisticsDB()

users_statistics.add_statistics(statistics_data={
    "firstname": f"{needed_users[0].firstname}",
    "lastname": f"{needed_users[0].lastname}",
    "school_class": f"{needed_users[0].school_class}"
})
users_statistics.add_statistics(statistics_data={
    "firstname": f"{needed_users[1].firstname}",
    "lastname": f"{needed_users[1].lastname}",
    "school_class": f"{needed_users[1].school_class}"
})

users_statistics.session.commit()