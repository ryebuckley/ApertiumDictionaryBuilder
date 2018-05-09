"""
Writes xml rules based off of a parallel corpus
"""
from word import Word
import optparse

#TODO sort out 0 todos below
#figure out how to get parrallel lists of word objects that aren't being translated

def main():
    #git input
    parser = optparse.OptionParser(description="dissimilarity map builder")

    parser.add_option('-a', '--lexL', type='string', help='The name of a file \
    storing the lexical tags for the left side language')

    parser.add_option('-b', '--lexR', type='string', help='The name of a file \
    storing the lexical tags for the right side language')

    parser.add_option('-d', '--dictionary', type='string', help='The name of a\
    file containing an apertium bilingual dictioary')

    (opts, args) = parser.parse_args()

    mandatories = ["lexL", "lexR", "dictionary"]

    for m in mandatories:
        if not opts.__dict__[m]:
            print('mandatory option ' + m + ' is missing\n')
            parser.print_help()
            sys.exit()

    #read dictionary into list
    dictionary = read_dictionary(opts.dictionary)
    #create lists of lexical tags
    langL_lex_tags = parse_lex_tags(opts.lexL)
    langR_lex_tags = parse_lex_tags(opts.lexR)

    # a list that will contain all generated entries
    entries = []

    ######test input
    # a word class for the left side of dict entry
    langL_word = Word("be<vbser><past><p3><sg>", 13)
    langL_word1 = Word("girl<n><sg>", 13)
    # a word class for the right side of dict entry
    langR_word = Word("Ser<vbser><inf>", 9)
    langR_word1 = Word("chico<n><f><sg>", 9)

    langL_words = [langL_word, langL_word1]
    langR_words = [langR_word, langR_word1]
    #####end test input

    #loops through parralel lusts of word objects and creates possible entries
    for langL_word,langR_word in zip(langL_words, langR_words):
        entry = build_entry(langL_word, langR_word, langL_lex_tags, langR_lex_tags)
        entries.append(entry)

    approve_entries(entries, dictionary)

    rewrite_dictionary(dictionary, opts.dictionary)

def write_entry(entry, dic):
    """
        given a dictionary entry and a list of lines from a dictioanry file
        adds the dictionary entry to the appropriate place in the list
    """
    #extract pos tag from entry
    pos_strt_ind = entry.index("<s")
    pos_end_ind = entry.index("/>")
    pos = entry[pos_strt_ind:pos_end_ind+2]  #dependent on a space between <s and n=""

    #find where to insert in dictioary
    line_num = -1
    for i,line in enumerate(dic):
        if pos in line:
            line_num = i
            break

    if line_num == -1:
        #this is the first instance of this pos
        for i in range(0,len(dic),-1):
            if "</section>" in dic[i]:
                line_num = i

    dic.insert(line_num, entry)

def approve_entries(entries, dictionary):
    """
        a command line interface that asks if an entry is valid, and if the
        entry is approved, calls a sub function which exports the entry to the
        dictionary
    """
    print("%d possible new dictionary entries" %len(entries))

    for i,entry in enumerate(entries):
        print("\nEntry %d of %d:"%(i+1, len(entries)))
        print("enter \"q\" at anytime to quit\n")
        print(entry)
        print("")
        approve = get_valid_approval()
        if approve == "y":
            write_entry(entry, dictionary)
        elif approve == "q":
            print("Thank you for using our program")
            exit(0)
        else:
            #entry = n, continue as if nothing happened
            pass

def get_valid_approval():
    """
        asks if entry is valid, checks to make sure answer is y/n
        returns answer
    """
    valid = ["y", "n", "q"]
    approve = input("Is this entry valid? y/n ")
    while approve not in valid:
        print("Please enter a lowercase \"n\", \"y\" or \"q\"")
        approve = input("Is this entry valid? y/n ")
    return approve

def build_entry(langL_word, langR_word, langL_lex_tags, langR_lex_tags):
    """
        given two word objects and two lists of lexical tags builds an xml
        dictionary entry
    """
    start = "\t <e><p><l>" + langL_word.word
    end = "</r></p></e>"
    mid = "</l><r>" + langR_word.word

    #which analysis to use for entry
    index = 0

    #fill in tags on left side
    for tag in langL_word.analyses[index]: #TODO replace that zero with something good
        if tag in langL_lex_tags:
            start += "<s n=\"" + tag  + "\"/>"

    #trust me this is necessary
    end_tags = ""
    #fill in tas on the right side
    for tag in langR_word.analyses[index]: #TODO replace zero with something good
        if tag in langR_lex_tags:
            end_tags += "<s n=\"" + tag  + "\"/>"

    entry = start + mid + end_tags + end + "\n"

    return entry


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

def rewrite_dictionary(dictionary, filename ):
    """
    takes in a list of lines and writes them to a given filename
    """
    try:
        f = open(filename, "w")
    except(IOError):
        print("Could not open dictionary file")
        exit(1)

    f.writelines(dictionary)
    f.close()


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


if __name__ == '__main__':
    main()
