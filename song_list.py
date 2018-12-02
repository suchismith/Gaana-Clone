class Song_list:
    def __init__(self, heading, songs):
        self.title = heading
        self.list_of_songs = songs

class Discover_list:
    def __init__(self, heading , get_url , data_list):
        self.heading = heading
        self.get_url = get_url
        self.data_list = data_list

class Profile_list:
    def __init__(self, heading , data_list):
        self.heading = heading
        self.data_list = data_list

class Profile_data:
    def __init__(self,title , username_list , userid_list):
        self.title = title
        self.username_list = username_list
        self.userid_list = userid_list

class Profile_to_send:
    def __init__(self, name, email):
        self.user_name = name
        self.email_id = email
