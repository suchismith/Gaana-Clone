from flask import Flask, json,jsonify,render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import Models
import songs
import song_list
import sqlite3
import flask_login
from flask_login import login_user, logout_user, current_user , login_required

app = Flask(__name__)
app.config['SONG_FOLDER'] = 'static/data/songs'
app.config['IMAGES_FOLDER'] = 'static/data/images'
app.config['DEFAULT_IMAGE'] = 'static/data/images/default.png'
app.config['TEMP_IMAGE_FOLDER'] = 'static/data/images/temp'
app.config['SECRET_KEY'] = "supersecretkey"
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Index


class User(flask_login.UserMixin):
    def __init__(self, id, name=None):
        self.email_id = id
        self.name = name

    def get_id(self):
        return self.email_id


@login_manager.user_loader
def load_user(id):
    id, name = Models.get_user(id)
    if id is None:
        return None
    user = User(id, name)
    return user
# Register Form Class

class RegisterForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


class LoginForm(Form):
    username = StringField('username', [validators.Length(min=6, max=50)])
    password = StringField('password', [validators.Length(min=4, max=25)])


@app.route('/uploadFile', methods=['POST'])
@login_required
def upload_song():
    print(request, request.files, request.form)
    song = songs.Song(request.form, request.files)
    song.add_song(current_user.email_id)
    return navbar()


def data_for_registered_user():
    favourite_songs = Models.get_favourite_songs(current_user.email_id)
    favourite_songs = song_details_to_send(favourite_songs)
    return song_list.Song_list("Favourite Songs", favourite_songs)


def details_of_trending_song():
    trending_songs = Models.get_trending_songs()
    print(trending_songs)
    if trending_songs is None:
        return None
    trending_songs = song_details_to_send(trending_songs)
    print(trending_songs)
    return song_list.Song_list("Trending Songs", trending_songs)


@app.route('/')
def index():
    # print(url_for('listArtists', my_var = 'abc'))
    register_form = RegisterForm(request.form)
    login_form = LoginForm(request.form)
    logged_in = False
    if current_user.is_authenticated:
        logged_in = True
    print(logged_in)
    return render_template('index.html', logged_in=logged_in,  register_form=register_form, login_form=login_form)

@app.route('/get_songs')
def send_data():
    data = []
    if current_user.is_authenticated:
        data.append(data_for_registered_user())
    data.append(details_of_trending_song())
#    print(data)
#    print(data[1].list_of_songs)
    return jsonify(data1 = render_template('base.html', data = data))

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        data = {}
        data['email_id'] = form.email.data
        data['user_name'] = form.username.data
        data['password'] = sha256_crypt.encrypt(str(form.password.data))
        success, message = Models.add_user(data)
        if success is True:
            flash(message, 'success')
            user = User(data['email_id'])
            print("success")
            login_user(user)
        else:
            flash(message, 'danger')
    return navbar()
    # send_data()


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("I am in login")
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate:
        # Get Form Fields
        success, message = Models.verify_user(form.username.data, form.password.data)
        if success is True:
            user = User(form.username.data)
            login_user(user)
            print("success")
            flash(message, 'success')
        else :
            flash(message, 'danger')
    return navbar()
    
@app.route('/navbar', methods=['GET'])
def navbar():
    register_form = RegisterForm(request.form)
    login_form = LoginForm(request.form)
    logged_in = False
    if current_user.is_authenticated:
        logged_in = True
    return jsonify(data1 = render_template('includes/navbar.html' , logged_in=logged_in,  register_form=register_form, login_form=login_form),data2=logged_in)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return navbar()


@app.route('/discover')
@login_required
def discover():

    data = []
    data.append(song_list.Discover_list("artist", "listArtists", Models.retrieve_artist()))
    data.append(song_list.Discover_list("genre", "listGenres", Models.retrieve_genre()))
    return jsonify(data1=render_template('discover.html', data=data))


@app.route('/artist')
@login_required
def listArtists():
    artist = request.args.get('my_var', None)
    list1 = Models.retrieve_songs_artist_genre('artist', artist)
    list1 = song_details_to_send(list1)
    print(artist+"hey")
    print("list retrieved",list1)
    data = song_list.Song_list(artist, list1)
    print(data.list_of_songs)
    return jsonify(data1 = render_template('artist.html', data=data))


@app.route('/genre')
@login_required
def listGenres():
    genre = request.args.get('my_var', None)
    list1 = Models.retrieve_songs_artist_genre('genre', genre)
    list1 = song_details_to_send(list1)
    data = song_list.Song_list(genre, list1)
    print("list retrieved",list1)
    print(data.list_of_songs)
    return jsonify(data1 = render_template('genre.html', data=data))


@app.route('/search')
@login_required
def search():
    query = request.args['query']
    songs_list = Models.get_matching_songs(query)
    songs_list = song_details_to_send(songs_list)
    artist_list = Models.get_matching_artist(query)
    print(songs_list, artist_list)
    return jsonify(data1 = render_template('search_result.html', song_list = songs_list, artist_list = artist_list))

@app.route('/search_loader')
@login_required
def search_loader():
    return jsonify(data1 = render_template('search_layout.html'))

def song_details_to_send(song_list):
    result = []
    for songid in song_list:
        song_details = Models.retrieve_song_details(songid)
        current_song = songs.Song_to_send(song_details['song_id'],song_details['song_name'], song_details['image_path'])
        result.append(current_song)
    return result


@app.route('/radio')
@login_required
def radio():
    print("here in radio")
    data = []
    list_of_songs = []
    mode_playlist = ["workout" , "devotional" , "party"]
    for list_of_mode in mode_playlist:
        list_of_songs = Models.retrieve_songs_mode(list_of_mode)
        data.append(song_list.Song_list(list_of_mode, list_of_songs))

    return  jsonify(data1=render_template('radio.html', data=data))


@app.route('/mymusic')
@login_required
def mymusic():
    email_id = current_user.email_id
    data_playlist = [] 
    table_name_playlist_track = get_playlist_track_name(email_id)
    table_name_playlist = get_playlist_name(email_id)
    data_playlist = Models.retrieve_playlist_table_track(table_name_playlist_track)
    data=[]
    final_list = []
    for list1 in data_playlist:
        list2 = Models.retrieve_songs_playlist(table_name_playlist,list1)
        final_list = song_details_to_send(list2)
        data.append(song_list.Song_list(list1, final_list))
    print(data)
    return jsonify(data1 = render_template('mymusic.html', data=data))

def get_playlist_track_name(tablename):
    return "\'"+tablename + "_playlist_track\'"

def get_playlist_name(tablename):
    return "\'"+tablename + "_playlist\'"

@app.route('/profile')
@login_required
def profile_details():
    id = current_user.email_id
    profile_details = Models.retrieve_user_details(id)
    print(profile_details, id)
    id = song_list.Profile_to_send(profile_details['user_name'],profile_details['email_id'])
    data = []
    data.append("Followers")
    data.append("Following")
    data.append("Uploaded")
    data.append("Downloaded")
    data.append("All_Users")
    print("here")
    return jsonify(data1 = render_template('profile.html',data=data, user = id))

@app.route('/song_list')
@login_required
def song_list_function():
    query = request.args.get('query')
    table_name_playlist = get_playlist_name(current_user.email_id)
    print(query, table_name_playlist)
    data = Models.retrieve_songs_playlist(table_name_playlist, query)
    data = song_details_to_send(data)
    print(data)
    return jsonify(data1 = render_template('song_list.html', heading = query, data = data))

@app.route('/view_profile')
@login_required
def view_profile():
    user = request.args.get('user')
    return jsonify(render_template('other_profile.html', user = user))

@app.route('/create_playlist', methods=['POST'])
# @login_required
def create_playlist():
    print("here")
    data = request.form['playlist_name']
    print(data)
    user = current_user.email_id
    table_name = get_playlist_track_name(user)
    Models.insert_playlist_table_track(table_name, data)
    return jsonify(data = True)

def profile_details_to_send(profile_list):
    result = []
    for profile_id in profile_list:
        profile_details = Models.retrieve_user_details(profile_id)
        current_song = song_list.Profile_to_send(profile_details['user_name'],profile_details['email_id'])
        result.append(current_song)
    return result

@app.route('/people_list')
@login_required
def people_list():
    data = []
    query = request.args.get('query')
    if query == 'follower':
        id = current_user.email_id
        data = Models.get_followers(id)
        data = profile_details_to_send(data)
    elif query == 'following':
        id = current_user.email_id
        data = Models.get_following(id)
        data = profile_details_to_send(data)
    else:
        query = 'List of All users'
        temp, data = Models.retrieve_users()
        data = profile_details_to_send(data)

    return jsonify(data1 = render_template('profile_helper.html', data = data, heading = query ))

@app.route('/profile_helper2')
@login_required
def profile_helper2():
    list1 = []
    user_id = request.args.get('my_var', None)
    dict1 = Models.retrieve_user_details(user_id)
    list1.append(dict1['email_id'])
    list1.append(dict1['user_name'])
    return jsonify(data1 = render_template('base.html', data=list1))

@app.route('/follow')
@login_required
def add_follower():
    following_id = request.args.get('my_var', None)
    Models.add_follower(current_user.email_id,following_id)
    return True

@app.route('/add_to_playlist')
@login_required
def add_to_playlist():
    id = current_user.email_id
    playlist_name = request.args.get('playlist_name',None)
    song_id = request.args.get('song_name',None)
    song_id = song_id.split('/')[-1]
    table_name = get_playlist_name(id)
    Models.add_song_to_playlist_not_upload(song_id, playlist_name, table_name)

@app.route('/get_playlist_list')
@login_required
def get_playlist_list():
    table_name = get_playlist_track_name(current_user.email_id)
    data = Models.retrieve_playlist_table_track(table_name)
    print(data)
    return jsonify(data = data)

@app.route('/increment_count')
def increment_count():
    print("increment")
    song_id = request.get.args('song_name')
    song_id = song_id.split('/')[-1]
    if song_id is not None:
        Models.increment_count(song_id)
    return True

@login_manager.unauthorized_handler
def unauthorized_callback():
    return send_data()

if __name__ == '__main__':
    app.run(debug=True,port='5001')
