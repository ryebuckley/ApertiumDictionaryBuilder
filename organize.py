from subprocess import Popen, PIPE
import optparse
import urllib.request, os, nltk, sys
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

import matplotlib
matplotlib.rcParams['font.size'] = 20.0

from word import Word
from entry import Entry
from interface_helpers import *

#ENGLISH_TEXT = "corpora/littleredridinghood.en" # 'corpora/udhr.en' # 'corpora/test.en'
#SPANISH_TEXT = "corpora/littleredridinghood.es" # 'corpora/udhr.sp' # 'corpora/test.sp'
#EN_ES_PATH = "../apertium/apertium-en-es/"
#EN_PATH = "../apertium/apertium-eng/"
BASE_URL = "http://swoogle.umbc.edu/SimService/GetSimilarity?operation=api&"
PIE_OUT_FILE = "analysis_pie.png"

DEFAULT_THRESH = 0.2
THRESH_DICT = {
    'vblex': 0.7,
    'vbmod': 0.7,
}

STOP_WORDS = list(stopwords.words('english'))

def main():

    print("\nWelcome to our text aligner\n")

    dictionary, L_lex_tags, R_lex_tags, Lcorpus, Rcorpus, Llanguage, Rlanguage, bilanguage, Ltransducer, Ttransducer, dict_file = startup()

    left = readData(Lcorpus, Ltransducer, Llanguage + "-tagger")
    right_trans = readData(Rcorpus, Ttransducer, bilanguage + "-postchunk")

    left_sents = getSentences(left)
    right_trans_sents = getSentences(right_trans)

    total_left_sents = sum([len(sent) for sent in left_sents])

    # assert(len(left_sents) == len(right_trans_sents))

    pie_chart_vals = []
    total_matches = []
    left_reduced, right_reduced = [], []
    for i in range(len(left_sents)):
        left, right = left_sents[i], right_trans_sents[i]
        entries, left_words, right_words = compareParagraph(left, right)
        used_words = [w.word for w in entries]

        match_count = sum([w.getNumMatches() for w in entries])
        total_matches.append(match_count)
        left_red = reduceParagraph(used_words, left_words)
        right_red = reduceParagraph(used_words, right_words)

        left_reduced.append(left_red)
        right_reduced.append(right_red)

    print("")
    evalCoverage(total_left_sents, sum(total_matches), "Total initial match percentage: ")
    pie_chart_vals.append(sum(total_matches))
    print("")

    ### now tag comparison phase / synonym analysis

    left_syn_reduced, right_syn_reduced = [], []
    for i in range(len(left_reduced)):
        left_red, left_red = left_reduced[i], right_reduced[i]
        matches = checkSynonmyms(left_red, right_red)
        total_matches[i] += len(matches)

        used_words_left = list(set([m[0].word for m in matches]))
        used_words_right = [m[1].word for m in matches]

        left_2_reduced = reduceParagraph(used_words_left, left_red)
        right_2_reduced = reduceParagraph(used_words_right, right_red)

        left_syn_reduced.append(left_2_reduced)
        right_syn_reduced.append(right_2_reduced)

    print("")
    evalCoverage(total_left_sents, sum(total_matches), "Total synonym match percentage: ")
    pie_chart_vals.append(sum(total_matches))
    print("")

    ### now remove common words

    left_final, right_final = [], []
    for i in range(len(left_syn_reduced)):
        left_final_red = list(set(reduceParagraph(STOP_WORDS, left_2_reduced)))
        right_final_red = list(set(reduceParagraph(STOP_WORDS, right_2_reduced)))

        num_removed_words = len(left_2_reduced) - len(left_final_red)
        total_matches[i] += num_removed_words

        left_final.append(left_final_red)
        right_final.append(right_final_red)

    evalCoverage(total_left_sents, sum(total_matches), "Final match percentage: ")
    pie_chart_vals.append(sum(total_matches))
    print("")

    print("Unmatched left words: ")
    print(list(set([w for paragraph in left_final for w in paragraph])))
    print('')
    print("Unmatched right words: ")
    print(list(set([w for paragraph in right_final for w in paragraph])))

    createPieChart(pie_chart_vals, total_left_sents)


def readData(text, apertium_path, apertium_command):
    """Reads raw data from apertium tagger/translator
    params: text    -   text from some corpus saved as .txt
            apertium_path   -   path to apertium directory
            apertium_command    -   command for translating/tagging
    returns: parsed translation
    """

    p1 = Popen(["cat", text], stdout=PIPE)
    p2 = Popen(["apertium", "-d", apertium_path, apertium_command], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    translation = p2.communicate()[0]
    translation = translation.decode()
    translation = translation.split("^")

    return translation

def getSentences(text):
    """Parse sentences in input text and return as list of lists
    params: text    -   text from apertium tagger
    returns: sents  -   list of lists of sentences
    """

    sents, tmp = [], []
    for i, phrase in enumerate(text):
        if '\n\n' in phrase:
            if tmp:
                sents.append(tmp)
                tmp = []
        elif i == len(text) - 1 and tmp:
            sents.append(tmp)
        elif phrase:
            tmp.append(phrase)

    return sents

def compareParagraph(left, right):
    """Direct comparison of same words in both texts
    params: left -   left tagged sentences
            right  -   right translated tagged senteces
    returns: nothing; prints evaluation statistic
    """

    left_words = translateParagraph(left)
    right_words = translateParagraph(right)

    # print left_words
    # print right_words

    pairs = directCompare(left_words, right_words)

    seen_words, entries = [], []
    for i, p in enumerate(pairs):
        if p[0] not in seen_words:
            e = Entry(p[0])
            entries.append(e)
            seen_words.append(p[0])
            e.addRightIndices(p[2])
        else:
            for ent in entries:
                if ent.word == p[0]:
                    e = ent
        e.addLeftIndex(p[1])

    for e in entries:
        e.collectMatches()

    return entries, left_words, right_words

def translateParagraph(p):
    """Make each word from paragraph a Word instance
    params: p   -   input paragraph of tagged text
    returns: list of Word instances
    """

    return [Word(w, i) for i, w in enumerate(p)]

def directCompare(left, right):
    """Pair up words translated to the same words in left language
    params: left -   list of word objects for left words
            right  -   list of word objects from translated right to left
    returns: pairs  -   [matched word, index of matched word, translated match indices]
    """

    pairs = []
    for i, w1 in enumerate(left):
        curr_indices = []
        for j, w2 in enumerate(right):
            if w1.word == w2.word:
                curr_indices.append(j)

        if curr_indices:
            pairs.append([w1.word, i, curr_indices])

    return pairs

def evalCoverage(wd_ls_len, match_count, message):
    """Evaluate how well matching did
    params: wd_ls   -   length of all words in corpus or paragraph
            match_count -   number of matches
            message     -   to be printed out to user
    returns: nothing; prints statistic
    """

    pct = float(match_count) / wd_ls_len
    print(message + "%.3f" % pct)

def reduceParagraph(used_words, word_ls):
    """Take out already matched words from list of word instances
    params: used_words  -   list of words that have already been matched
            word_ls     -   list of word instances
    returns: list of unmatched words
    """

    return [wd for wd in word_ls if wd.word not in used_words]

def createURL(w1, w2):
    """Create URL pattern for querying swoogle API
    params: w1 & w2 -   word instances
    returns: completed URL pattern for querying
    """

    w1 = w1.word.replace(' ', '%20')
    w2 = w2.word.replace(' ', '%20')
    w1 = w1.replace('#', '')
    w2 = w2.replace('#', '')
    w1 = urllib.parse.quote(w1)
    w2 = urllib.parse.quote(w2)
    url = BASE_URL + 'phrase1=' + w1 + '&' + 'phrase2=' + w2
    return url

def checkSynonmyms(left_list, right_list):
    """Checks for synonyms in two lists of word instances
    params: left_list    -   list of word instances in left language
            right_list     -   list of word instances from translated right language
    returns:
    """

    matches = []
    for i, w1 in enumerate(left_list):
        base_pos = getPartsOfSpeech(w1)

        for j, w2 in enumerate(right_list):
            sub_pos = getPartsOfSpeech(w2)

            # compare parts of speech
            same_pos = compareLists(base_pos, sub_pos)
            if same_pos:
                left_pct = i / float(len(left_list))
                right_pct = j / float(len(right_list))

                # compare relative positions in text
                if abs(left_pct - right_pct) < 0.20:
                    page = urllib.request.urlopen(createURL(w1, w2))
                    score = float(page.read())

                    # check if score is above threshold
                    if score > THRESH_DICT.get(same_pos[0], DEFAULT_THRESH):
                        matches.append((w1, w2, score, i, j))

    return matches

def getPartsOfSpeech(w):
    """Get first lemma/lemmae for a give Word instance
    params: w   -   Word instance
    returns: list of parts of speech
    """

    return [ls[0] for ls in w.analyses if ls]

def compareLists(ls1, ls2):
    """Compare two lists to see if there are any matches
    params: ls1 & ls2   -   two lists
    returns: matches    -   list of common elements in ls1 and ls2
    """

    matches = []
    for item in ls1:
        if item in ls2:
            matches.append(item)
    return matches

def createPieChart(vals, total_sents):
    """Create pie chart of matching progress
    params: vals    -   list of numbers of matches at each step of main()
            total_sents   -   total number of sentences
    returns: nothing; creates pie chart
    """

    remaining = total_sents - vals[-1]
    labels = ["direct translation", "synonym", "stopwords", "remaining"]
    vals[1] -= vals[0]
    vals[2] -= vals [0] - vals[1]
    sizes = [l / float(total_sents) for l in vals]
    sizes.append(remaining / float(total_sents))
    explode = [0, 0, 0, 0.1]

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax.axis('equal')
    # ax.set_title('Breakdown of Text Aligner Analysis')

    plt.savefig(PIE_OUT_FILE)

def startup():
    #git input
    parser = optparse.OptionParser(description="entry interace")

    parser.add_option('-f', '--lexL', type='string', help='The name of a file \
    storing the lexical tags for the left side language')

    parser.add_option('-g', '--lexR', type='string', help='The name of a file \
    storing the lexical tags for the right side language')

    parser.add_option('-c', '--Lcorpus', type='string', help='The name of a file \
    storing the parallel corpus for the left side language')

    parser.add_option('-e', '--Rcorpus', type='string', help='The name of a file \
    storing the parallel corpus for the right side language')

    parser.add_option('-d', '--dictionary', type='string', help='The name of a\
    file containing an apertium bilingual dictionary')

    parser.add_option('-l', '--Llanguage', type='string', help='The language \
    code of the left side language')

    parser.add_option('-r', '--Rlanguage', type='string', help='The language \
    code of the right side language')

    parser.add_option('-b', '--bilanguage', type='string', help='The language \
    code of the translation pair')

    parser.add_option('-v', '--Ltransducer', type='string', help='Path to \
    transducer for left side language')

    parser.add_option('-t', '--Ttransducer', type='string', help='Path to \
    translation transducer')

    (opts, args) = parser.parse_args()

    mandatories = ["lexL", "lexR", "Lcorpus", "Rcorpus", "dictionary", "Llanguage", "Rlanguage", \
    "bilanguage", "Ltransducer", "Ttransducer"]

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

    return dic, Ltags, Rtags, opts.Lcorpus, opts.Rcorpus, opts.Llanguage, opts.Rlanguage, opts.bilanguage,\
    opts.Ltransducer, opts.Ttransducer, opts.dictionary

if __name__ == '__main__':
    main()
