from random import randint
from modules.databases.UsersDB import Users, UsersDB
from modules.databases.UsersStatisticsDB import UsersStatistics, UsersStatisticsDB


new_user: dict[str, str] = {
    "firstname": "Test user",
    "lastname": "",
    "sex": "without sex",
    "school_class": "11Z",
    "username": "test_user",
    "password": "(test#user)",
    "rank": "student",
}

new_user_statistics: dict[str, str] = {
    "firstname": "Test user",
    "lastname": "",
    "school_class": "11Z",
    "q_type_1": "0&0&0",
    "q_type_2": "0&0&0",
    "q_type_3": "0&0&0",
    "q_type_4": "0&0&0",
    "q_type_5": "0&0&0",
    "q_type_6": "0&0&0",
    "q_type_7": "0&0&0",
    "q_type_8": "0&0&0",
    "q_type_9": "0&0&0",
    "q_type_10": "0&0&0",
    "q_type_11": "0&0&0",
    "q_type_12": "0&0&0",
    "q_type_13": "0&0&0",
    "q_type_14": "0&0&0",
    "q_type_15": "0&0&0",
    "q_type_16": "0&0&0",
    "q_type_17": "0&0&0",
    "q_type_18": "0&0&0",
    "q_type_19": "0&0&0",
    "q_type_20": "0&0&0",
    "q_type_21": "0&0&0",
    "q_type_22": "0&0&0",
    "q_type_23": "0&0&0",
    "q_type_24": "0&0&0",
    "q_type_25": "0&0&0",
    "q_type_26": "0&0&0",
    "q_type_27": "0&0&0"
}

data_to_change = {
    "q_type_1": "0&0&0",
    "q_type_2": "0&0&0",
    "q_type_3": "0&0&0",
    "q_type_4": "0&0&0",
    "q_type_5": "0&0&0",
    "q_type_6": "0&0&0",
    "q_type_7": "0&0&0",
    "q_type_8": "0&0&0",
    "q_type_9": "0&0&0",
    "q_type_10": "0&0&0",
    "q_type_11": "0&0&0",
    "q_type_12": "0&0&0",
    "q_type_13": "0&0&0",
    "q_type_14": "0&0&0",
    "q_type_15": "0&0&0",
    "q_type_16": "0&0&0",
    "q_type_17": "0&0&0",
    "q_type_18": "0&0&0",
    "q_type_19": "0&0&0",
    "q_type_20": "0&0&0",
    "q_type_21": "0&0&0",
    "q_type_22": "0&0&0",
    "q_type_23": "0&0&0",
    "q_type_24": "0&0&0",
    "q_type_25": "0&0&0",
    "q_type_26": "0&0&0",
    "q_type_27": "0&0&0"
}

for data in data_to_change:
    c_v = randint(35, 100)
    r_v = randint(20, 100)
    while c_v < r_v:
        r_v = randint(20, 100)
    data_to_change[data] = [
        c_v,
        r_v
    ]

# UsersDB().add_instance(user_data=new_user)
# UsersStatisticsDB().add_statistics(statistics_data=new_user_statistics)
UsersStatisticsDB().change_statistics(id=1, data_to_change=data_to_change)
