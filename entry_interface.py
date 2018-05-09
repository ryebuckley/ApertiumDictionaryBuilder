"""
Contains a tool that when given a word in one language, and a word in another,
suggests a dictioanry entry, and upon approval of that entry by the user,
adds it to a given dictioary file
"""

from word import Word
import optparse
from subprocess import *

#TODO sort out 0 todos below
def main():
    dictionary, L_lex_tags, R_lex_tags, Llanguage, Rlanguage, Ltransducer, Rtransducer, dict_file = startup()
    print("Welcome to the dictionary entry automator tool")
    
    print("enter \"q!\" at anytime to quit")
    Llemma = input("Word in %s: "%Llanguage)
    if Llemma != "q!":
        Rlemma = input("Word in %s: "%Rlanguage)

    while(Llemma != "q!" and Rlemma != "q!"):
        Lword = process_word(Llemma, Ltransducer, Llanguage)
        Rword = process_word(Rlemma, Rtransducer, Rlanguage)

        rules = generate_rules(Lword, Rword, L_lex_tags, R_lex_tags)
        approve_entries(rules, dictionary)
        rewrite_dictionary(dictionary, dict_file)

        print("enter \"q!\" at anytime to quit")
        Llemma = input("Word in %s: "%Llanguage)
        if Llemma != "q!":
            Rlemma = input("Word in %s: "%Rlanguage)

    print("Thank you for using our tool, we hope you found it useful")

def generate_rules(L, R, Ltags, Rtags):
    """
        takes in two word objects with equivalent lemmas and figures
        out by part of speech with analysis are equivalent, and then makes
        dictionary entries
    """
    entries = []
    #line up by part of speech
    for i,a in enumerate(L.analyses):
        for j,b in enumerate(R.analyses):
            if a[0] == b[0]:
                #build rule
                entry = build_entry(L, R, Ltags, Rtags, i, j)
                entries.append(entry)
    return entries

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

def build_entry(Lword, Rword, Ltags, Rtags, Lindex, Rindex):
    """
        given two word objects and two lists of lexical tags builds an xml
        dictionary entry
    """
    start = "\t <e><p><l>" + Lword.word
    end = "</r></p></e>"
    mid = "</l><r>" + Rword.word

    #fill in tags on left side
    for tag in Lword.analyses[Lindex]: #TODO replace that zero with something good
        if tag in Ltags:
            start += "<s n=\"" + tag  + "\"/>"

    #trust me this is necessary
    end_tags = ""
    #fill in tas on the right side
    for tag in Rword.analyses[Rindex]: #TODO replace zero with something good
        if tag in Rtags:
            end_tags += "<s n=\"" + tag  + "\"/>"

    entry = start + mid + end_tags + end + "\n"

    return entry

def process_word(lemma, transducer, language):
    """
        given a word, a language and a transducer
        runs the word throught the transducer and build a word object
        returns a word object
    """

    p1 = Popen(["echo", lemma], stdout=PIPE)
    p2 = Popen(["apertium", "-d", transducer, language+"-morph"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output=p2.communicate()[0]
    output = output.decode()

    #parse
    strt_ind = output.index("^")
    end_ind = output.index("$")
    output = output[strt_ind+1:end_ind]

    w = Word(output,0)
    return w

def startup():
    #git input
    parser = optparse.OptionParser(description="entry interace")

    parser.add_option('-a', '--lexL', type='string', help='The name of a file \
    storing the lexical tags for the left side language')

    parser.add_option('-b', '--lexR', type='string', help='The name of a file \
    storing the lexical tags for the right side language')

    parser.add_option('-d', '--dictionary', type='string', help='The name of a\
    file containing an apertium bilingual dictioary')

    parser.add_option('-l', '--Llanguage', type='string', help='The language \
    code of the left side language')

    parser.add_option('-r', '--Rlanguage', type='string', help='The language \
    code of the right side language')

    parser.add_option('-t', '--Ltransducer', type='string', help='Path to \
    transducer for left side language')

    parser.add_option('-v', '--Rtransducer', type='string', help='Path to \
    transducer for right side language')

    (opts, args) = parser.parse_args()

    mandatories = ["lexL", "lexR", "dictionary", "Llanguage", "Rlanguage", \
    "Ltransducer", "Rtransducer"]

    for m in mandatories:
        if not opts.__dict__[m]:
            print('mandatory option ' + m + ' is missing\n')
            parser.print_help()
            sys.exit()

    #read dictionary into list
    dic = read_dictionary(opts.dictionary)

    #create lists of lexical tags
    Ltags = parse_lex_tags(opts.lexL)
    Rtags = parse_lex_tags(opts.lexR)

    return dic, Ltags, Rtags, opts.Llanguage, opts.Rlanguage, opts.Ltransducer,\
     opts.Rtransducer, opts.dictionary

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
