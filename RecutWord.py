from flask import json
class RecutWord:

    def __init__(self, word: str, start: float, stop: float, confidence: float):
        self.word = word
        self.start = start
        self.stop = stop
        self.confidence = confidence

    def getStart(self) -> float:
        return self.start

    def getStop(self) -> float:
        return self.stop

    def getWord(self) -> str:
        return self.word

    def getConfidence(self) -> float:
        return self.confidence

    def serialize(self):
        return {
            'word': self.word,
            'start': self.start,
            'stop': self.stop,
            'confidence': self.confidence,
        }


def loadRecutWordsFromFile(fileName: str) -> list[RecutWord]:
    print(fileName)
    file = open(fileName, "r")
    fileContents: str = file.read()
    file.close()
    filesLines = fileContents.split('\n')
    listOfRecutWords = []
    for record in filesLines:
        values = record.split(' ')
        listOfRecutWords.append(RecutWord(values[0], float(values[1]), float(values[2]), float(values[3])))
    return listOfRecutWords


def saveRecutWordsToFile(fileName: str, words: list[RecutWord]):
    file = open(fileName, "w")
    listOfRecutWordsAsString = [" ".join([w.getWord(), str(w.getStart()), str(w.getStop()), str(w.getConfidence())]) for w in words]
    stringOfRecutWords = '\n'.join(listOfRecutWordsAsString)
    file.writelines(stringOfRecutWords)
    file.close()
