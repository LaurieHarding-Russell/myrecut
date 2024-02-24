import wave
from os.path import join

import numpy as np
from moviepy.editor import *
import deepspeech
from RecutWord import RecutWord


class RecutProcess:

    def __init__(self, fileName: str, PATH_TO_RESOURCES: str):
        self.fileName = fileName
        self.PATH_TO_RESOURCES = PATH_TO_RESOURCES

    def processAllWordsInClip(self) -> list[RecutWord]:
        tempFileName = join(self.PATH_TO_RESOURCES, self.fileName + ".mp4")
        movie = VideoFileClip(tempFileName)
        textFrames: deepspeech.Metadata = self.__getTextMetadataFromMovie(movie)
        return self.__findAllPossibleWords(textFrames.transcripts)

    def __getTextMetadataFromMovie(self, movie: VideoClip) -> deepspeech.Metadata:
        data16 = self.__getAudioAsDeepspeechAudioInput(movie)
        model = self.__setupModel()
        return model.sttWithMetadata(data16, num_results=1)

    def __setupModel(self) -> deepspeech.Model:
        pathToPbmm = os.path.join(self.PATH_TO_RESOURCES, "external/pmml/file/deepspeech-0.9.3-models.pbmm")
        pathToScorer = os.path.join(self.PATH_TO_RESOURCES, "external/scorer/file/deepspeech-0.9.3-models.scorer")
        model = deepspeech.Model(pathToPbmm)
        model.enableExternalScorer(pathToScorer)
        # for word in text:
        #     # https://deepspeech.readthedocs.io/en/master/HotWordBoosting-Examples.html
        #     model.addHotWord(word, 10)
        return model

    def __getAudioAsDeepspeechAudioInput(self, movie: VideoClip):
        fileName = self.fileName + ".wav"
        movie.audio.write_audiofile(fileName, fps=16000, nbytes=2, ffmpeg_params=["-ac", "1"])
        fin = wave.open(fileName, 'rb')
        frames = fin.getnframes()
        buffer = fin.readframes(frames)
        return np.frombuffer(buffer, dtype=np.int16)

    def __findAllPossibleWords(self, textFrames: list[deepspeech.CandidateTranscript]) -> list[RecutWord]:
        wordsInFrames: list[RecutWord] = []
        for frame in textFrames:
            wordsInFrames.extend(self.__analyzeFrameForWords(frame))
        return wordsInFrames

    @staticmethod
    def __analyzeFrameForWords(frame: deepspeech.CandidateTranscript) -> list[RecutWord]:
        token: deepspeech.TokenMetadata
        buildWord: str = ""
        recutWords: list[RecutWord] = []
        startTime = None
        for tokenIndex, token in enumerate(frame.tokens):
            if token.text == " ":
                if len(buildWord) > 0:
                    if len(frame.tokens) > tokenIndex + 1:
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
