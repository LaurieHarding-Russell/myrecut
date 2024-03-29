import math
from io import BytesIO
from math import floor
from os import listdir
from os.path import isfile, join

from flask import Flask, send_from_directory, request, send_file, jsonify, make_response
from moviepy.editor import *
from werkzeug.datastructures import FileStorage
from RecutProcess import RecutProcess
from RecutService import recutIt
from RecutWord import RecutWord, loadRecutWordsFromFile, saveRecutWordsToFile

app = Flask(__name__, static_url_path="")

PATH_TO_RESOURCES = os.path.dirname(__file__)
DEEP_SPEECH_TIME_STEP = 0.2
PARITION_TIME = 60 * 5

allWordClips: dict[str, list[RecutWord]] = {}
recutFolder = join(PATH_TO_RESOURCES, "recutAnalysis")


def init():
    global allWordClips
    if os.path.exists(recutFolder):
        allFiles = [f for f in listdir(recutFolder) if isfile(join(recutFolder, f))]
        for fileName in allFiles:
            allWordClips[fileName] = loadRecutWordsFromFile(os.path.join(recutFolder, fileName))
    else:
        os.mkdir(recutFolder)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/state", methods=['GET'])
def getState():
    global allWordClips
    dictValue = {}
    for x in allWordClips:
        dictValue[x] = [value.serialize() for value in allWordClips[x]]
    return jsonify(dictValue)


@app.route("/analyze", methods=['POST'])
def processMovie():
    global allWordClips
    file: FileStorage = request.files.get("file")
    filename = file.filename.split('.')[0]
    file.save(join(PATH_TO_RESOURCES, file.filename))  # Moviepy requires us to save to a file since its calling commands on your machine to do the actual work :(
    tempFileName = join(PATH_TO_RESOURCES, file.filename)
    movie = VideoFileClip(tempFileName)

    numberOfTenMinuteParts = math.ceil(movie.duration / PARITION_TIME)
    partOutMovies(filename, movie, numberOfTenMinuteParts)

    for i in range(0, numberOfTenMinuteParts):
        partFileName = filename + str(i)
        process = RecutProcess(fileName=partFileName, PATH_TO_RESOURCES=PATH_TO_RESOURCES)
        allWordClips[partFileName] = process.processAllWordsInClip()
        saveRecutWordsToFile(os.path.join(recutFolder, partFileName), allWordClips.get(partFileName))
    return getState()


def partOutMovies(filename, movie, parts):
    for i in range(0, parts):
        temp: VideoClip
        if i == parts - 1:
            temp = movie.subclip(i * PARITION_TIME, movie.duration - 1)
        else:
            temp = movie.subclip(i * PARITION_TIME, PARITION_TIME * (i + 1))
        temp.write_videofile(filename + str(i) + '.mp4', codec='libx264', logger=None)


@app.route("/recut", methods=['POST'])
def recut():
    global allWordClips
    text: list[str] = request.json["text"].split(" ")
    recutMovie = recutIt(text, allWordClips, PATH_TO_RESOURCES)
    if isinstance(recutMovie, list):
        make_response("Missing parts of :: " + " ".join(recutMovie), 400)
    return send_file(BytesIO(recutMovie), download_name="recut.mp4", as_attachment=True)


if __name__ == "__main__":
    from waitress import serve
    init()
    serve(app, host="0.0.0.0", port=8080)
