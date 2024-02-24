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


def recutIt(text: list[str], allWordClips: dict[str, list[RecutWord]]) -> recutResultVar:
    recutText = text.copy()
    wordClips = []
    for key in allWordClips:
        __searchClipForLargestLeftLeaningChunks(allWordClips, key, recutText, wordClips)

    if len(recutText) > 0:
        raise "error can't get all words"
    return __soundClipsToMovieClips(wordClips)


def __searchClipForLargestLeftLeaningChunks(allWordClips, key, recutText, wordClips):
    searchable = True
    while searchable and len(recutText) > 0:
        largestLeftLeaningClip = __findClipForLargestLeftLeaningChunk(key, allWordClips[key], recutText)
        if largestLeftLeaningClip.index == 0:
            searchable = False
        else:
            wordClips.append(largestLeftLeaningClip)
            recutText = recutText[largestLeftLeaningClip.index:]


def __soundClipsToMovieClips(wordClips: list[ClipLocation]) -> AnyStr:
    clips = []
    for wordClip in wordClips:
        movie = VideoFileClip(wordClip.movie)
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
            print(clip.index)
            if clip.connected and text[clip.index] == recutWord.getWord():
                clip.end = recutWord
                clip.index = clip.index + 1
                if clip.index >= len(text):
                    return clip
            else:
                clip.connected = False
        if recutWord.getWord() == text[0]:
            clipLocation.append(ClipLocation(recutWord, 1, movie))
    return __findLargestClip(clipLocation)


def __findLargestClip(clipLocation) -> ClipLocation:
    largestClip = ClipLocation([], 0, "")
    for location in clipLocation:
        if largestClip.index < location.index:
            largestClip = location
    return largestClip
