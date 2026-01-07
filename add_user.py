from modules.databases.UsersDB import Users, UsersDB


new_user: dict[str, str] = {
    "firstname": "Test user",
    "lastname": "",
    "sex": "without sex",
    "school_class": "11Z",
    "username": "test_user",
    "password": "(test#user)",
    "rank": "student",
}

UsersDB().add_instance(user_data=new_user)