

class Word(object):
    def __init__(self, raw, position):
        self.raw = raw
        self.position = position
        self.__get_attrs()
        print (self.word, self.analyses)

    def __str__(self):
        return self.word

    def __repr__(self):
        return self.word

    def __get_attrs(self):
        """Get attributes and word of raw input line
        params: none
        returns: nothing
        """

        # if line comes from tagger
        if '/' in self.raw:
            parsed = self.raw.split('/')
            if len(parsed) > 1:
                parsed = parsed[1:]

            start_idx = parsed[0].index('<')
            self.word = parsed[0][:start_idx]

        # if line comes from translator
        else:
            start_idx = self.raw.index('<')
            self.word = self.raw[:start_idx]
            parsed = [self.raw[start_idx:]]

        self.analyses = []
        for i in range(len(parsed)):
            start_idx = parsed[i].index('<')
            analysis = parsed[i][start_idx+1:].replace('>', '')
            analysis = analysis.replace('$', '')
            analysis = analysis.replace(' ', '')
            split_pos = analysis.split('<')

            self.analyses.append(split_pos)
