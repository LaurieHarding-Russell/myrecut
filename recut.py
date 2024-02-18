from io import BytesIO

from flask import Flask, send_from_directory, request, send_file
from moviepy.editor import *
from werkzeug.datastructures import FileStorage

app = Flask(__name__, static_url_path="")

TEMP_FILE_NAME = "temp.mp4"


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/recut", methods=['POST'])
def recut():
    file: FileStorage = request.files.get("file")
    file.save(
        TEMP_FILE_NAME)  # this is stupid and wont work with multiple requests. moviePy should be ok with it all being in memory :(
    movie = VideoFileClip(TEMP_FILE_NAME)

    text = request.form.get("text")
    sound = getSoundFromMovie(file)
    textFrames = getTextFramesFromSound(sound)
    soundFrames = findLargestChunkOfSoundFromText(textFrames, text)
    recutMovie = soundClipsToMovieClips(movie, soundFrames)

    return send_file(BytesIO(recutMovie), download_name="recut.mp4", as_attachment=True)


def getSoundFromMovie(movie):
    return ""


def getTextFramesFromSound(sound):
    return [""]


def findLargestChunkOfSoundFromText(textFrames, text):
    return [""]


def soundClipsToMovieClips(movie: VideoFileClip, soundFrames):
    clip: VideoFileClip = movie.subclip(500, 600)
    clip.write_videofile('recut.mp4', codec='libx264', logger=None)
    data = None
    with open('recut.mp4', 'rb') as file:
        data = file.read()
    return data


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
