from flask import Flask, render_template, request
import json
import os
import Models
app = Flask(__name__)


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class A:
    def __init__(self, x, y):
        self.image_path = x
        self.song_path = y

@app.route('/')
def root():
    return render_template('sample.html')
@app.route('/base')
def hello():
    a = A('index3.jpeg', '1.mp3')
    b = A('index2.jpeg', '2.mp3')
    list1 = []
    i = 0
    while i < 10:
        i += 1
        list1.append(a)
    list1.append(b)
    list1.append(b)
    list1.append(b)

    return render_template('base.html', list1=list1)


@app.route('/discover')
def discover():
    #	list_of_genre=["rock","pop","romance"]
    #	list_of_artist=["sonu nigam","arijit"]
    list_of_genre = []
    list_of_genre = Models.retrieve_genre()
    list_of_artist = []
    list_of_artist = Models.retrieve_artist()
    return render_template('discover.html', list1=list_of_genre, list2=list_of_artist)


@app.route('/discover/<variable>')
def genres(variable):
    return '<h1>you clicked'+variable+'</h1>'


@app.route('/upload')
def upload():
    message = ""
    return render_template('upload.html', message=message)


@app.route('/artist')
def listArtists():

    artist = request.args.get('my_var', None)
    list1 = []
    list1 = Models.retrieve_songs_artist_genre('artist', artist)
    return render_template('base.html', list1=list1)


@app.route('/genre')
def listGenre():

    genre = request.args.get('my_var', None)
    list1 = []
    list1 = Models.retrieve_songs_artist_genre('genre', genre)
    return render_template('base.html', list1=list1)


# @app.route('/artist')
# def listArtists():

#     artist = request.args.get('my_var', None)
#     list1 = []
#     list1 = Models.retrieve_songs_artist_genre('artist', artist)
#     return render_template('base.html', list1=list1)


# @app.route('/genre')
# def listGenre():

#     genre = request.args.get('my_var', None)
#     list1 = []
#     list1 = Models.retrieve_songs_artist_genre('genre', genre)
#     return render_template('base.html', list1=list1)


@app.route('/uploadFile', methods=['POST'])
def uploadFile():
    target = APP_ROOT+'/audio'

    if not os.path.isdir(target):
        os.mkdir(target)
    filename = ""
#	destination=""
    try:
        for file in request.files.getlist("audiofile"):
            filename = file.filename
            target = target+"/"+filename

            file.save(target)
            message = "Files Uploaded Succesfully"+request.form['artist']

            return render_template('messages.html', message=message), '302'
    except:
        message = "Error in uploading"
        return render_template('messages.html', message=message)


app.run(debug=True, port='5004')
