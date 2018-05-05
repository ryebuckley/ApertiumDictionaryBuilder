import os


READ_FILE = "test.txt"
READ_DIR = ""

def main():

    
    file_path = os.path.join(READ_DIR, READ_FILE)

    # assume this is just one paragraph
    # we will want to break up by paragraph
    
    allwords, enwords, spwords = ([] for _ in range(3))
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            allwords.append(line) if line else None

    for i in range(len(allwords)):
        w = Word(allwords[i], i)
        if i % 2 == 0:
            enwords.append(w)
        else:
            spwords.append(w)
    
    


    # organize by place in paragraph, pos, ...

class Word(object):
    def __init__(self, raw, position):
        self.raw = raw
        self.position = position

        self.__get_attrs()

    def __get_attrs(self):
        """Get attributes and word of raw input line
        params: none
        returns: nothing
        """

        parsed = self.raw.split('/')
        if len(parsed) > 1:
            parsed = parsed[1:]
        
        start_idx = parsed[0].index('<')
        self.word = parsed[0][:start_idx]

        self.analyses = []
        for i in range(len(parsed)):
            start_idx = parsed[i].index('<')
            analysis = parsed[i][start_idx+1:].replace('>', '')
            split_pos = analysis.split('<')
            
            self.analyses.append(split_pos)

        
            

        
        
if __name__ == '__main__':
    main()
