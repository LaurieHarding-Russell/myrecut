import wave
from io import BytesIO

import numpy as np
from flask import Flask, send_from_directory, request, send_file, make_response
from moviepy.editor import *
from werkzeug.datastructures import FileStorage
import deepspeech

app = Flask(__name__, static_url_path="")

TEMP_FILE_NAME = "temp.mp4"


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# noinspection PyTypeChecker
@app.route("/recut", methods=['POST'])
def recut():
    file: FileStorage = request.files.get("file")
    file.save(
        TEMP_FILE_NAME)  # Moviepy requires us to save to a file since its calling commands on your machine to do the actual work :(
    movie = VideoFileClip(TEMP_FILE_NAME).subclip(3, 23)
    text: list[str] = request.form.get("text").split(" ")

    textFrames: deepspeech.Metadata = getTextMetadataFromMovie(movie, text)
    soundFrames = findLargestChunkOfSoundFromText(textFrames.transcripts, text)
    recutMovie = soundClipsToMovieClips(movie, soundFrames)

    if recutMovie is None:
        return make_response("Could not find text and make movie", 400)
    return send_file(BytesIO(recutMovie), download_name="recut.mp4", as_attachment=True)


def getTextMetadataFromMovie(movie: VideoClip, text: list[str]) -> deepspeech.Metadata:
    # movie.audio.write_audiofile("temp.wav", nbytes=2, codec='pcm_s16le')
    movie.audio.write_audiofile("temp.wav", 16000, 2, 2000, "pcm_s16le")
    ws = os.path.dirname(__file__)
    pathToPbmm = os.path.join(ws, "external/pmml/file/deepspeech-0.9.3-models.pbmm")
    pathToScorer = os.path.join(ws, "external/scorer/file/deepspeech-0.9.3-models.scorer")
    # fin = librosa.load('test.wav', sr=16000)
    fin = wave.open('temp.wav', 'rb')
    frames = fin.getnframes()
    buffer = fin.readframes(frames)

    data16 = np.frombuffer(buffer, dtype=np.int16)

    model = deepspeech.Model(pathToPbmm)
    model.enableExternalScorer(pathToScorer)
    for word in text:
        # https://deepspeech.readthedocs.io/en/master/HotWordBoosting-Examples.html
        model.addHotWord(word, 10)
    text = model.sttWithMetadata(data16, num_results=10)
    print(model.stt(data16))
    return text


def findLargestChunkOfSoundFromText(textFrames: list[deepspeech.CandidateTranscript], text: list[str]) -> list[tuple[int, int]]:
    frames: list[tuple[int, int]] = []
    for word in text:
        for frame in textFrames:
            start, end = analyzeFrameForWords(frame, word)
            if start is not None:
                # raise Exception("Can't find word " + word)
                frames.append((start, end))

    return frames


def analyzeFrameForWords(frame: deepspeech.CandidateTranscript, word: str) -> tuple[int, int]:
    token: deepspeech.TokenMetadata
    buildWord: str = ""
    startTime = None
    endTime = 0
    for token in frame.tokens:
        if token.text == "":
            if len(buildWord) > 0:
                endTime = token.start_time
            buildWord = ""
            startTime = None
        else:
            buildWord = buildWord + token.text
            if startTime is None:
                startTime = token.start_time

    if token.text == word:
        return startTime, endTime
    return None, None


def soundClipsToMovieClips(movie: VideoFileClip, soundFrames: list[deepspeech.TokenMetadata]):
    clips = []
    for frame in soundFrames:
        clips.append(movie.subclip(frame.start_time(), frame.start_time() + 1))

    if len(clips) == 0:
        return None
    finalClip = concatenate_videoclips(clips)

    finalClip.write_videofile('recut.mp4', codec='libx264', logger=None)
    with open('recut.mp4', 'rb') as file:
        data = file.read()
    return data


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=8080)
