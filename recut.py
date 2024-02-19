from collections import Counter
from io import BytesIO
from itertools import groupby

from flask import Flask, send_from_directory, request, send_file, make_response
from moviepy.editor import *
from werkzeug.datastructures import FileStorage
from multiprocessing import Pool
from RecutProcess import RecutProcess
from RecutWord import RecutWord

app = Flask(__name__, static_url_path="")

TEMP_FILE_NAME = "temp.mp4"
PATH_TO_RESOURCES = os.path.dirname(__file__)
DEEP_SPEECH_TIME_STEP = 0.2


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/recut", methods=['POST'])
def recut():
    text: list[str] = request.form.get("text").split(" ")
    file: FileStorage = request.files.get("file")

    tempFileName = "temp0.mp4"
    file.save(tempFileName)  # Moviepy requires us to save to a file since its calling commands on your machine to do the actual work :(
    movie = VideoFileClip(tempFileName)

    process = RecutProcess(text=text, tempId="0", PATH_TO_RESOURCES=PATH_TO_RESOURCES)
    allWordClips = process.processAllWordsInClip()
    wordClip, missingWords = findClipLocationsForWords(allWordClips, text)

    if len(missingWords) > 0:
        return make_response("Could not find the following words " + ','.join(missingWords), 400)
        # return make_response("Could not find the following words " + ','.join(missingWords) +
        #                      " words: " + ",".join(map(lambda a : a.getWord(), allWordClips)), 400)

    recutMovie = soundClipsToMovieClips(movie, wordClip)

    return send_file(BytesIO(recutMovie), download_name="recut.mp4", as_attachment=True)


def findClipLocationsForWords(wordsInFrames: list[RecutWord], text: list[str]) -> tuple[list[RecutWord], list[str]]:
    wordClips: list[RecutWord] = []
    wordsNotFound: list[str] = []

    for word in text:
        for recutWord in wordsInFrames:
            if word == recutWord.getWord():  # Fixme, maybe should make it random instead of grabbing first.
                wordClips.append(recutWord)
                break
        if len(wordClips) == 0 or word != wordClips[-1].getWord():
            wordsNotFound.append(word)

    return wordClips, wordsNotFound


def soundClipsToMovieClips(movie: VideoFileClip, wordClips: list[RecutWord]):
    clips = []
    for wordClip in wordClips:
        clips.append(movie.subclip(wordClip.getStart(), wordClip.getStop()))
    finalClip = concatenate_videoclips(clips)

    finalClip.write_videofile('recut.mp4', codec='libx264', logger=None)
    with open('recut.mp4', 'rb') as file:
        data = file.read()
    return data

if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
