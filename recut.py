import wave
from io import BytesIO
import numpy as np
from flask import Flask, send_from_directory, request, send_file, make_response
from moviepy.editor import *
from werkzeug.datastructures import FileStorage
import deepspeech
from recutWord import RecutWord

app = Flask(__name__, static_url_path="")

TEMP_FILE_NAME = "temp.mp4"
PATH_TO_RESOURCES = os.path.dirname(__file__)
DEEP_SPEECH_TIME_STEP = 0.2

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/recut", methods=['POST'])
def recut():
    file: FileStorage = request.files.get("file")
    file.save(TEMP_FILE_NAME)  # Moviepy requires us to save to a file since its calling commands on your machine to do the actual work :(
    movie = VideoFileClip(TEMP_FILE_NAME).subclip(3, 23)
    text: list[str] = request.form.get("text").split(" ")

    textFrames: deepspeech.Metadata = getTextMetadataFromMovie(movie, text)
    allWordClips = findAllPossibleWords(textFrames.transcripts)
    wordClip, missingWords = findClipLocationsForWords(allWordClips, text)
    if len(missingWords) > 0:
        return make_response("Could not find the following words " + ','.join(missingWords), 400)

    recutMovie = soundClipsToMovieClips(movie, wordClip)

    return send_file(BytesIO(recutMovie), download_name="recut.mp4", as_attachment=True)


def getTextMetadataFromMovie(movie: VideoClip, text: list[str]) -> deepspeech.Metadata:
    data16 = getAudioAsDeepspeechAudioInput(movie)
    model = setupModel(text)
    return model.sttWithMetadata(data16, num_results=10)


def setupModel(text: list[str]) -> deepspeech.Model:
    pathToPbmm = os.path.join(PATH_TO_RESOURCES, "external/pmml/file/deepspeech-0.9.3-models.pbmm")
    pathToScorer = os.path.join(PATH_TO_RESOURCES, "external/scorer/file/deepspeech-0.9.3-models.scorer")
    model = deepspeech.Model(pathToPbmm)
    model.enableExternalScorer(pathToScorer)
    # for word in text:
    #     # https://deepspeech.readthedocs.io/en/master/HotWordBoosting-Examples.html
    #     model.addHotWord(word, 10)
    return model


def getAudioAsDeepspeechAudioInput(movie: VideoClip):
    movie.audio.write_audiofile("temp.wav", fps=16000, nbytes=2, ffmpeg_params=["-ac", "1"])
    fin = wave.open('temp.wav', 'rb')
    frames = fin.getnframes()
    buffer = fin.readframes(frames)
    return np.frombuffer(buffer, dtype=np.int16)


def findAllPossibleWords(textFrames: list[deepspeech.CandidateTranscript]) -> list[RecutWord]:
    wordsInFrames: list[RecutWord] = []
    for frame in textFrames:
        wordsInFrames.extend(analyzeFrameForWords(frame))
    return wordsInFrames


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


def analyzeFrameForWords(frame: deepspeech.CandidateTranscript) -> list[RecutWord]:
    token: deepspeech.TokenMetadata
    buildWord: str = ""
    recutWords: list[RecutWord] = []
    startTime = None
    for tokenIndex, token in enumerate(frame.tokens):
        if token.text == " ":
            if len(buildWord) > 0:
                if frame.tokens[tokenIndex + 1]:
                    endTime = frame.tokens[tokenIndex + 1].start_time
                else:
                    endTime = token.start_time
                recutWords.append(RecutWord(word=buildWord, start=startTime, stop=endTime, confidence=frame.confidence))
            buildWord = ""
            startTime = None
        else:
            buildWord = buildWord + token.text
            if startTime is None:
                if tokenIndex - 1 >= 0:
                    startTime = frame.tokens[tokenIndex - 1].start_time
                else:
                    startTime = token.start_time

    return recutWords


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
