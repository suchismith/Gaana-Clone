import sqlite3 as sql
import sys, os
from passlib.hash import sha256_crypt
from heapq import heappush, heappop, heappushpop
import distance

import songs
def sanatize(s):
    return "\'" + s + "\'"

def create():
    try:
        with sql.connect("gaana.db") as con:
            print("Opened database successfully")
            con.execute('''
                   CREATE TABLE users (email_id TEXT NOT NULL PRIMARY KEY, 
                   user_name TEXT NOT NULL, 
                   password TEXT NOT NULL);
                ''')
            print ("Opened database successfully 1")
            con.execute('''
                   CREATE TABLE songs (song_id TEXT NOT NULL PRIMARY KEY, 
                   song_path TEXT NOT NULL,
                   song_name TEXT NOT NULL,
                   image_path TEXT NOT NULL,
                   genre TEXT NOT NULL,
                   artist TEXT,
                   year INTEGER DEFAULT 0,
                   count INTEGER DEFAULT 0);
                ''')
            print ("Opened database successfully 2")
            con.execute('''
                   CREATE TABLE followers (follower_id TEXT NOT NULL, 
                   following_id TEXT NOT NULL,
                   PRIMARY KEY (follower_id,following_id));
                ''')
            print ("Table created successfully")
            con.close()
    except Exception as e:
        print ("Table already exists", e)


def add_user(kwargs):

    try:
        emailid = kwargs['email_id']
        msg = "Record successfully added"
        changed = False
        con = sql.connect('gaana.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM users  WHERE email_id = ?",(emailid,))
        row = cur.fetchone()
        print('work')
        if row:
            msg = "User with EmailId \'%s\' is already present, insertion failed!" % (
                emailid)
        else:
            print("here")
            cur.execute('''INSERT INTO users (user_name, email_id, password) 
                            VALUES (:user_name, :email_id, :password)''', kwargs)
            msg = "User added successfully"
            print("done successfully")
            changed = True
            con.commit()
            con.close()
        if changed is True:
            table_name = sanatize(emailid + "_playlist")
            table_name2 = sanatize(emailid + "_playlist_track")
            add_playlist_table(table_name)
            add_playlist_table_track(table_name2)
        return (True, msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = "Unexpected Error in insert operation 1" + str(e)
        print (msg)
        return (False, msg)


def verify_user(emailid, password):
    con = sql.connect("gaana.db")
    cursor = con.cursor()
    print(password, emailid)
    cursor = con.execute("SELECT email_id, password FROM users")
    for row in cursor:
        if row[0] == emailid and sha256_crypt.verify(password, row[1]):
            return True, "Login Successfull"
    return False, "Invalid Credentials"

def get_user(email_id):
    con = sql.connect("gaana.db")
    cur = con.cursor()
    cur.execute("SELECT * from users WHERE email_id = ?",(email_id,))
    row = cur.fetchone()
    if row is None:
        return None, None
    return row[0], row[1]

####################################################################################################################################


def add_playlist_table(table_name):
    try:
        # with sql.connect("gaana.db") as con:
        con = sql.connect('gaana.db')
        con.execute('''
                    CREATE TABLE %s (playlist_name TEXT NOT NULL, 
                    song_id TEXT,
                    PRIMARY KEY(playlist_name,song_id));
                    '''% (table_name))
        con.commit()
        print ("Table created successfully")
    except Exception as e:
        print ("Table already exists ", e)

def add_playlist_table_track(table_name):
    try:
        # with sql.connect("gaana.db") as con:
        con = sql.connect('gaana.db')
        con.execute('''
                    CREATE TABLE %s (playlist_name TEXT PRIMARY KEY);
                    '''% (table_name))
        print ("Table created successfully")
        con.commit()
        con.execute("INSERT into %s (playlist_name) VALUES ('upload'),('download'),('favourites')" %(table_name))
        con.commit()
        print("Inserted playlist successfully ")
    except Exception as e:
        print ("Table already exists ", e)
        
def insert_playlist_table_track(table_name,playlist_name):
    try:
      #  table_name = sanatize(table_name)
        print(table_name)
        print(playlist_name)
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("SELECT playlist_name FROM %s where playlist_name=?" %(
            table_name),( playlist_name,))
        row = cur.fetchone()
        playlist_name=sanatize(playlist_name)
        if not row:
            cur.execute("INSERT INTO %s VALUES (%s)" %
                        (table_name,playlist_name))
            con.commit()
            con.close()
        return not row
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = "Unexpected Error in insert operation 1" + str(e)
        print (msg)
        return (False, msg)

def add_playlist(table_name, playlist_name):
    try:
        if(playlist_name == "upload" or playlist_name == "download" or playlist_name == "favourites"):
            pass
        else:
            insert_playlist_table_track(table_name,playlist_name)
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("SELECT playlist_name FROM %s where playlist_name=\'%s\'" % (
            table_name, playlist_name))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO %s playlist_name VALUES %s" %
                        (table_name, playlist_name))
            con.commit()
            print("Added playlist "+playlist_name +
                  " successfully in "+table_name)
        con.close()
        return not row
    except:
        print("This Playlist already exists for "+table_name+" user")


def add_song_to_playlist(song, playlist_name, tablename):

    try:
        tablename = sanatize(tablename)
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM %s where playlist_name = ? and song_id = ? " %
                    (tablename),( playlist_name, song.song_id,))
        row = cur.fetchone()
        con.close()
        if not row:
            if(playlist_name == "upload"):
                upload_song(song)
            common_add_method(song, playlist_name, tablename)
        else:
            print("Entry already exists")
        return not row
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = "Unexpected Error in insert operation 1" + str(e)
        print(msg)

def add_song_to_playlist_not_upload(song, playlist_name, tablename):

    try:
        tablename = sanatize(tablename)
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM %s where playlist_name = ? and song_id = ? " %
                    (tablename),( playlist_name, song,))
        row = cur.fetchone()
        con.close()
        if not row:
            con = sql.connect("gaana.db")
            cur = con.cursor()
            print(tablename, playlist_name, song)
            cur.execute("INSERT INTO %s (playlist_name , song_id ) VALUES (?,?)" %
                        (tablename), (playlist_name, song,))
            print ("Added song in "+playlist_name +
                " for user "+tablename.split('_')[0])
            con.commit()
            con.close()
        else:
            print("Entry already exists")
        return not row
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = "Unexpected Error in insert operation 1" + str(e)
        print(msg)


def upload_song(song):
    dict = {}
    dict['song_id'] = song.song_id
    dict['song_path'] = song.song_path
    dict['song_name']=song.song_name
    dict['image_path'] = song.image_path
    dict['genre'] = song.genre
    dict['artist'] = song.artist
    dict['year'] = song.year
    dict['count'] = 0
    print(dict)
    add_song(dict)

def add_song(dict):
    try:
        print("In add song")
        song_id = dict['song_id']
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM songs where song_id = ?" , (song_id,))
        row = cur.fetchone()
        if not row:
            cur.execute('''INSERT INTO songs (song_id, song_path,song_name, image_path, genre, artist, year, count) 
                            VALUES (:song_id, :song_path, :song_name, :image_path, :genre, :artist, :year, :count)''', dict)
            print ("Added song successfully")
            con.commit()
        con.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = "Unexpected Error in insert operation 1" + str(e)

def common_add_method(song, playlist_name, tablename):
    print("here")
    try:
        con = sql.connect("gaana.db")
        cur = con.cursor()
        print(tablename, playlist_name, song.song_id)
        cur.execute("INSERT INTO %s (playlist_name , song_id ) VALUES (?,?)" %
                    (tablename), (playlist_name, song.song_id))
        print ("Added song in "+playlist_name +
               " for user "+tablename.split('_')[0])
        con.commit()
        con.close()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = "Unexpected Error in insert operation 1" + str(e)
        print(msg)


def add_to_favourites(song, email_id):
    email_id = email_id+"_playlist"
    email_id = sanatize(email_id)
    add_song_to_playlist(song, "favourites", email_id)


def add_to_download(song, email_id):
    email_id = email_id+"_playlist"
    email_id = sanatize(email_id)
    add_song_to_playlist(song, "download", email_id)

####################################################################################################################################


def add_follower(follower_id, following_id):
    try:
        attributes = "follower_id,following_id"
        values = sanatize(follower_id+","+following_id)
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("INSERT INTO followers (%s) VALUES (%s)" %
                    (attributes, values))
        print ("Follower "+follower_id+" added for "+following_id)
        con.close()
    except Exception as e:
        print ("Error occured ", e)


def get_followers(id):
    try:
        list_of_followers = []
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute(
            "Select follower_id from followers where following_id=\'%s\'" % (id))
        result = cur.fetchall()
        for row in result:
            list_of_followers.append(row[0])
        con.close()
        return list_of_followers
    except Exception as e:
        print ("Error occured ", e)


def get_following(id):
    try:
        list_of_following = []
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute(
            "Select following_id from followers where follower_id=\'%s\'" % (id))
        result = cur.fetchall()
        for row in result:
            list_of_following.append(row[0])
        con.close()
        return list_of_following
    except Exception as e:
        print ("Error occured ", e)

##################################################################################################################################


def retrieve_songs_artist_genre(value1, value2):

    # value1 - artist or genre category
    # value2 - specific value of artist/genre
    # Output - List of songs for given artist or genre.
    try:
        list_of_songs = []
        con = sql.connect("gaana.db")
        cur = con.cursor()
        print("here",value1)
        print("here1",value2)
        # value1 = sanatize(value1)
        cur.execute("Select song_id from songs where %s = ?"%
                    (value1), (value2,))
        result = cur.fetchall()
        for row in result:
            list_of_songs.append(row[0])
        con.close()
        print("returning list",list_of_songs)
        return list_of_songs
    except Exception as e:
        print ("Error occured ", e)


def retrieve_songs_playlist(value1, value2):

    # value1 - Table Name
    # value2 - Playlist name
    # Output - List of songs for given playlist name.
    try:
        list_of_songs = []
        con = sql.connect("gaana.db")
        cur = con.cursor()
        print(value1, value2)
        cur.execute("Select song_id from %s where playlist_name = ?"%(value1) 
                    , (value2,))
        result = cur.fetchall()
        for row in result:
            list_of_songs.append(row[0])
        con.close()
        return list_of_songs
    except Exception as e:
        print ("Error occured ", e)
        return []

def get_favourite_songs(email_id):
    email_id = email_id+"_playlist"
    email_id = sanatize(email_id)
    return retrieve_songs_playlist(email_id, "favourites")


def retrieve_songs_mode(mode):

    # value - list of genre in mode
    # Output - List of songs for given mode.
    try:
        list_of_songs = []
        list_of_genre = []
        if(mode == "workout"):
            list_of_genre = ["rock", "pop"]
        elif(mode == "devotional"):
            list_of_genre = ["bhakti", "sufi"]
        elif(mode == "party"):
            list_of_genre = ["rock", "metal","romance"]
        con = sql.connect("gaana.db")
        cur = con.cursor()
        for value in list_of_genre:
            cur.execute(
                "Select song_id from songs where genre = ?" % (value))
            result = cur.fetchall()
            for row in result:
                list_of_songs.append(row[0])
        con.close()
        return list_of_songs
    except Exception as e:
        print ("Error occured ", e)


# Given Song Id , it retrives song details.
# Output - Dictionary of song details
def retrieve_song_details(songid):

    try:
        dict_of_songs = {}
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("Select * from songs where song_id=\'%s\'" % (songid))
        result = cur.fetchall()
        for row in result:
            dict_of_songs['song_id'] = row[0]
            dict_of_songs['song_path'] = row[1]
            dict_of_songs['song_name'] = row[2]
            dict_of_songs['image_path'] = row[3]
            dict_of_songs['genre'] = row[4]
            dict_of_songs['artist'] = row[5]
            dict_of_songs['year'] = row[6]
            dict_of_songs['count'] = row[7]
        con.close()
        return dict_of_songs
    except Exception as e:
        print ("Error occured ", e)


def retrieve_genre():

    try:
        list_of_genre = []
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("Select DISTINCT genre from songs")
        result = cur.fetchall()
        print(result)
        for row in result:
            list_of_genre.append(row[0])
        con.close()
        return list_of_genre
    except Exception as e:
        print ("Error occured ", e)


def retrieve_artist():

    try:
        list_of_artist = []
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute("Select DISTINCT artist from songs")
        result = cur.fetchall()
        for row in result:
            list_of_artist.append(row[0])
        con.close()
        return list_of_artist
    except Exception as e:
        print ("Error occured ", e)


def get_trending_songs():
   try:
       list_of_songs = []
       con = sql.connect("gaana.db")
       cur = con.cursor()
       cur.execute("Select song_id from songs ORDER BY count DESC")
       result = cur.fetchall()
       for row in result:
           list_of_songs.append(row[0])
       con.close()
       return list_of_songs
   except Exception as e:
       print ("Error occured ", e)
       return None

def increment_count(songid):
    try:
        con = sql.connect("gaana.db")
        cur = con.cursor()
        cur.execute(
            "UPDATE songs SET count = count +1 where song_id =\'%s\'" % (songid))
        row = cur.fetchone()
        if(row):
            print("Updated count for song "+songid)
        con.close()
    except Exception as e:
        print ("Error occured ", e)

def retrieve_playlist_table_track(tablename):
   try:
       list_of_playlist = []
       con = sql.connect("gaana.db")
       cur = con.cursor()
       cur.execute("Select playlist_name from %s" %(tablename))
       result = cur.fetchall()
       for row in result:
           list_of_playlist.append(row[0])
       con.close()
       return list_of_playlist
   except Exception as e:
       print ("Error occured ", e)
       return None

def retrieve_users():
   try:
       list_of_username = []
       list_of_userid = []
       con = sql.connect("gaana.db")
       cur = con.cursor()
       cur.execute("Select user_name,email_id from users")
       result = cur.fetchall()
       for row in result:
           list_of_username.append(row[0])
           list_of_userid.append(row[1])           
       con.close()
       return list_of_username , list_of_userid
   except Exception as e:
       print ("Error occured ", e)
       return None



############################################################


def get_matching_songs(query):
    try:
        song_list = []
        con = sql.connect('gaana.db')
        cursor = con.execute('select song_name from songs')
        dictionary = {}
        for row in cursor:
            # for word in row[0]:
            word = row[0]
            if word in dictionary.keys():
                dictionary[word] = dictionary[word]+1
            else:
                dictionary[word] = 1
        cursor = con.execute('select song_name, song_id from songs')         
        for row in cursor:
            maximum_match = 0
            # for word in row[0]:
            word = row[0]
            result = distance.get_jaro_distance(query, word)
            result *= (1+0.001/float(dictionary[word]))
            maximum_match = max(maximum_match,result)
            if len(song_list) <10:
                heappush(song_list, (-maximum_match, row[1]))
            else:
                heappushpop(song_list, (-maximum_match, row[1]))
        result = []
        for data in song_list:
            result.append(data[1])
        return result
    except Exception as e:
        print(e)
        return None
    

def get_matching_artist(query):
    try:
        song_list = []
        con = sql.connect('gaana.db')
        cursor = con.execute('Select DISTINCT artist from songs')
        dictionary = {}
        for row in cursor:
            # for word in row[0]:
            word = row[0]
            if word in dictionary.keys():
                dictionary[word] = dictionary[word]+1
            else:
                dictionary[word] = 1
        cursor = con.execute('Select DISTINCT artist from songs')         
        for row in cursor:
            maximum_match = 0
            word = row[0]
            result = distance.get_jaro_distance(query, word)
            result *= (1+0.001/float(dictionary[word]))
            maximum_match = max(maximum_match,result)
            if len(song_list) <10:
                heappush(song_list, (-maximum_match, row[0]))
            else:
                heappushpop(song_list, (-maximum_match, row[0]))
        result = []
        for data in song_list:
            result.append(data[1])
        return result
    except Exception as e:
        print(e)
        return None
    

def retrieve_user_details(userid):
  try:
      dict={}
      con = sql.connect("gaana.db")
      cur = con.cursor()
      cur.execute("Select * from users where email_id =\'%s\'" % (userid))
      result = cur.fetchall()
      for row in result:
          dict['email_id']=row[0]
          dict['user_name']=row[1]
      con.close()
      return dict
  except Exception as e:
      print ("Error occured ", e)
      return None

if __name__ == '__main__':
    songs.song_id = "S1.hello46#%@@"
    common_add_method(songs,"Hey@ritik","hello")