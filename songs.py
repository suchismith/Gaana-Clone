import hashlib
from werkzeug import secure_filename
from flask import current_app
from flask_login import current_user
import os
import Models


def sha_hash(fname):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()

    with open(fname, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


ALLOWED_SONG_EXTENSIONS = set(['mp3'])
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_song(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_SONG_EXTENSIONS


def allowed_image(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_IMAGE_EXTENSIONS


class Song:
    def __init__(self, form, files):
        self.song_name = form['name']
        self.year = form['year']
        self.artist = form['artist']
        self.genre = form['genre']
        self.count = 0

        song_file = files['audiofile']
        image_file = files['image_file']

        if song_file and allowed_song(song_file.filename):
            filename = secure_filename(self.song_name + song_file.filename)
            temp_name = os.path.join(
                current_app.config['TEMP_IMAGE_FOLDER'], filename)
            song_file.save(temp_name)
            extension = song_file.filename.split('.')[-1].lower()
            hash_of_song_file = sha_hash(temp_name) + "." + extension
            if os.path.isfile(os.path.join(current_app.config['SONG_FOLDER'], hash_of_song_file)) is False:
                os.rename(temp_name, (os.path.join(current_app.config['SONG_FOLDER'], hash_of_song_file)))
            else:
                os.remove(temp_name)
            self.song_id = hash_of_song_file
            self.song_path = os.path.join(
                current_app.config['SONG_FOLDER'], hash_of_song_file)
            # os.remove(temp_name)
        else:
            self.song_id = None

        if image_file and allowed_image(image_file.filename):
            filename = secure_filename(self.song_name + image_file.filename)
            temp_name = os.path.join(
                current_app.config['TEMP_IMAGE_FOLDER'], filename)
            image_file.save(temp_name)
            extension = image_file.filename.split('.')[-1].lower()
            hash_of_image_file = sha_hash(temp_name) + "." + extension
            if os.path.isfile(os.path.join(current_app.config['IMAGES_FOLDER'], hash_of_image_file)) is False:
                os.rename(temp_name, (os.path.join(current_app.config['IMAGES_FOLDER'], hash_of_image_file)))
            else:
                os.remove(temp_name)
            self.image_id = hash_of_image_file
            self.image_path = os.path.join(
                current_app.config['IMAGES_FOLDER'], hash_of_image_file)
            # os.remove(temp_name)
        else:
            self.image_id = current_app.config['DEFAULT_IMAGE']

    def add_song(self, user):
        user = user + "_playlist"
        playlist_name = "upload"
        Models.add_song_to_playlist(self, playlist_name, user)


class Song_to_send:
    def __init__(self, song_id, name, image_path):
        self.song_id = song_id
        self.name = name
        self.song_path = os.path.join(
            current_app.config['SONG_FOLDER'], self.song_id)
        self.image_path = image_path
