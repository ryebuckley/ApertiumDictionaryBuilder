import numpy as np

class Entry(object):

    def __init__(self, word):
        self.word = word
        self.left_indices = []
        self.right_indices = []

    def __str__(self):
        return self.word

    def __repr__(self):
        return self.word

    def addLeftIndex(self, i):
        self.left_indices.append(i)

    def addRightIndices(self, ls):
        self.right_indices = ls

    def collectMatches(self):
        matches = []
        for idx in self.left_indices:
            dists = np.array([abs(idx - i) for i in self.right_indices])
            match_idx = np.argmin(dists)
            match = self.right_indices[match_idx]
            self.right_indices.pop(match_idx)
            matches.append((idx, match))
            if not self.right_indices:
                break

        self.matches = matches

    def getNumMatches(self):
        return len(self.left_indices)
