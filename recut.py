from flask import Flask, send_from_directory, request

app = Flask(__name__, static_url_path="")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/recut", methods=['POST'])
def recut():
    file = request.files.get("file")
    text = request.form.get("text")
    sound = getSoundFromMovie(file)
    textFrames = getTextFrameFromSound(sound)
    soundFrames = findLargestChunkOfSoundFromText(textFrames, text)
    return soundClipsToMovieClips(file, soundFrames)

def getSoundFromMovie(movie):
    return ""

def getTextFramesFromSound(sound):
    return [""]

def findLargestChunkOfSoundFromText(textFrames, text):
    return [""]

def soundClipsToMovieClips(file, soundFrames):
    return "";

if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
