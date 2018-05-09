import numpy as np

class Entry(object):

    def __init__(self, word):
        self.word = word
        self.eng_indices = []
        self.sp_indices = []

    def __str__(self):
        return self.word

    def __repr__(self):
        return self.word

    def addEnglighIndex(self, i):
        self.eng_indices.append(i)

    def addSpanishIndices(self, ls):
        self.sp_indices = ls

    def collectMatches(self):
        matches = []
        for idx in self.eng_indices:
            dists = np.array([abs(idx - i) for i in self.sp_indices])
            match_idx = np.argmin(dists)
            match = self.sp_indices[match_idx]
            self.sp_indices.pop(match_idx)
            matches.append((idx, match))
            if not self.sp_indices:
                break

        self.matches = matches

    def getNumMatches(self):
        return len(self.eng_indices)
