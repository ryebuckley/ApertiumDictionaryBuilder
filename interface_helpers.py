def read_dictionary(filename):
    """
    reads a dictioary file into a list of lines
    """
    try:
        f = open(filename, "r")
    except(IOError):
        print("Could not open dictionary file")
        exit(1)

    dic = f.readlines()
    f.close()

    return dic

def parse_lex_tags(filename):
    """
        reads through a given file containing only lexical tags and not
        morphological tags for a given language and reads them into a list
        for more information on how to build this file see the README.md
    """
    try:
        f= open(filename, "r")
    except(IOError):
        print("in parse_lex_tags")
        print("could not open dictionary file")
        exit(1)

    #initialize list
    lex_tags = []

    line = f.readline()
    while line:
        line = line.strip()
        #some simple syntax checking
        if line.isalpha():
            lex_tags.append(line)
        else:
            print("unexpected symbol found while parsing lexical tags")
            exit(1)

        line = f.readline()

    f.close()
    return lex_tags
