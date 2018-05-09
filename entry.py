class Entry(object):

    def __init__(self, word):
        self.word = word
        self.eng_indices = []
        self.sp_indices = []

    def addEnglighIndex(self, i):
        self.eng_indices.append(i)

    def addSpanishIndices(self, ls):
        self.sp_indices.append(ls)
