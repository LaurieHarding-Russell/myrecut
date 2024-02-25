from os.path import join
from typing import AnyStr, TypeVar

import RecutWord
from moviepy.editor import *


class ClipLocation:
    def __init__(self, start: RecutWord, index: int, movie: str):
        self.movie = movie
        self.start = start
        self.end = start
        self.index = index
        self.connected = True
    movie: str
    start: RecutWord
    end: RecutWord
    index: int
    connected: bool


recutResultVar = TypeVar('recutResultVar', bytes, str, list[str])


def recutIt(text: list[str], allWordClips: dict[str, list[RecutWord]], PATH_TO_RESOURCES) -> recutResultVar:
    recutText = text.copy()
    wordClips = []
    success = True

    for l in range(0, len(recutText)):
        for key in allWordClips:
            success = __searchClipForLargestLeftLeaningChunks(allWordClips, key, recutText, wordClips)

    if not success:
        raise "error can't get all words"
    return __soundClipsToMovieClips(wordClips, PATH_TO_RESOURCES)


def __searchClipForLargestLeftLeaningChunks(allWordClips, key, recutText, wordClips) -> list[str]:
    searchable = True
    while searchable and len(recutText) > 0:
        largestLeftLeaningClip = __findClipForLargestLeftLeaningChunk(key, allWordClips[key], recutText)
        if largestLeftLeaningClip.index == 0:
            searchable = False
        else:
            wordClips.append(largestLeftLeaningClip)
        recutText = recutText[largestLeftLeaningClip.index:]
    return recutText


def __soundClipsToMovieClips(wordClips: list[ClipLocation], PATH_TO_RESOURCES) -> AnyStr:
    clips = []
    for wordClip in wordClips:
        movie = VideoFileClip(join(PATH_TO_RESOURCES, wordClip.movie + ".mp4"))
        clips.append(movie.subclip(wordClip.start.getStart(), wordClip.end.getStop()))
    finalClip = concatenate_videoclips(clips)

    finalClip.write_videofile('recut.mp4', codec='libx264', logger=None)
    data: AnyStr
    with open('recut.mp4', 'rb') as file:
        data = file.read()
    return data


def __findClipForLargestLeftLeaningChunk(movie: str, wordsInFrames: list[RecutWord], text: list[str]) -> ClipLocation:
    clipLocation: list[ClipLocation] = []
    for recutWord in wordsInFrames:
        for clip in clipLocation:
            if clip.connected and text[clip.index] == recutWord.getWord():
                clip.end = recutWord
                clip.index = clip.index + 1
                if clip.index >= len(text):
                    return clip
            else:
                clip.connected = False
        if recutWord.getWord() == text[0]:
            startClip = ClipLocation(recutWord, 1, movie)
            if 1 >= len(text):
                return startClip
            clipLocation.append(startClip)
    return __findLargestClip(clipLocation)


def __findLargestClip(clipLocation) -> ClipLocation:
    largestClip = ClipLocation([], 0, "")
    for location in clipLocation:
        if largestClip.index < location.index:
            largestClip = location
    return largestClip
