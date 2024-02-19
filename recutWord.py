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
