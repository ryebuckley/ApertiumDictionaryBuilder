from subprocess import Popen, PIPE
import urllib.request, os, nltk, sys
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

import matplotlib
matplotlib.rcParams['font.size'] = 20.0

from word import Word
from entry import Entry

ENGLISH_TEXT = "corpora/littleredridinghood.en" # 'corpora/udhr.en' # 'corpora/test.en'
SPANISH_TEXT = "corpora/littleredridinghood.es" # 'corpora/udhr.sp' # 'corpora/test.sp'
EN_ES_PATH = "../apertium/apertium-en-es/"
EN_PATH = "../apertium/apertium-eng/"
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

    eng = readData(ENGLISH_TEXT, EN_PATH, "eng-tagger")
    sp_trans = readData(SPANISH_TEXT, EN_ES_PATH, "es-en-postchunk")

    eng_sents = getSentences(eng)
    sp_trans_sents = getSentences(sp_trans)

    total_eng_sents = sum([len(sent) for sent in eng_sents])

    # assert(len(eng_sents) == len(sp_trans_sents))

    pie_chart_vals = []
    total_matches = []
    eng_reduced, sp_reduced = [], []
    for i in range(len(eng_sents)):
        eng, sp = eng_sents[i], sp_trans_sents[i]
        entries, eng_words, sp_words = compareParagraph(eng, sp)
        used_words = [w.word for w in entries]

        match_count = sum([w.getNumMatches() for w in entries])
        total_matches.append(match_count)
        evalCoverage(len(eng), match_count, "\tInitial match percentage: ")
        eng_red = reduceParagraph(used_words, eng_words)
        sp_red = reduceParagraph(used_words, sp_words)

        eng_reduced.append(eng_red)
        sp_reduced.append(sp_red)

    print("")
    evalCoverage(total_eng_sents, sum(total_matches), "Total initial match percentage: ")
    pie_chart_vals.append(sum(total_matches))
    print("")

    ### now tag comparison phase / synonym analysis

    eng_syn_reduced, sp_syn_reduced = [], []
    for i in range(len(eng_reduced)):
        eng_red, sp_red = eng_reduced[i], sp_reduced[i]
        matches = checkSynonmyms(eng_red, sp_red)
        total_matches[i] += len(matches)
        evalCoverage(len(eng_sents[i]), total_matches[i], "\tAfter synonym analysis: ")

        used_words_eng = list(set([m[0].word for m in matches]))
        used_words_sp = [m[1].word for m in matches]

        eng_2_reduced = reduceParagraph(used_words_eng, eng_red)
        sp_2_reduced = reduceParagraph(used_words_sp, sp_red)

        eng_syn_reduced.append(eng_2_reduced)
        sp_syn_reduced.append(sp_2_reduced)

    print("")
    evalCoverage(total_eng_sents, sum(total_matches), "Total synonym match percentage: ")
    pie_chart_vals.append(sum(total_matches))
    print("")

    ### now remove common words

    eng_final, sp_final = [], []
    for i in range(len(eng_syn_reduced)):
        eng_final_red = list(set(reduceParagraph(STOP_WORDS, eng_2_reduced)))
        sp_final_red = list(set(reduceParagraph(STOP_WORDS, sp_2_reduced)))

        num_removed_words = len(eng_2_reduced) - len(eng_final_red)
        total_matches[i] += num_removed_words

        eng_final.append(eng_final_red)
        sp_final.append(sp_final_red)

    evalCoverage(total_eng_sents, sum(total_matches), "Final match percentage: ")
    pie_chart_vals.append(sum(total_matches))
    print("")

    print("Unmatched engligh words: ")
    print(list(set([w for paragraph in eng_final for w in paragraph])))
    print('')
    print("Unmatched spanish words: ")
    print(list(set([w for paragraph in sp_final for w in paragraph])))

    createPieChart(pie_chart_vals, total_eng_sents)


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

def compareParagraph(eng, sp):
    """Direct comparison of same words in both texts
    params: eng -   english tagged sentences
            sp  -   spanish translated tagged senteces
    returns: nothing; prints evaluation statistic
    """

    eng_words = translateParagraph(eng)
    sp_words = translateParagraph(sp)

    # print eng_words
    # print sp_words

    pairs = directCompare(eng_words, sp_words)

    seen_words, entries = [], []
    for i, p in enumerate(pairs):
        if p[0] not in seen_words:
            e = Entry(p[0])
            entries.append(e)
            seen_words.append(p[0])
            e.addSpanishIndices(p[2])
        else:
            for ent in entries:
                if ent.word == p[0]:
                    e = ent
        e.addEnglighIndex(p[1])

    for e in entries:
        e.collectMatches()

    return entries, eng_words, sp_words

def translateParagraph(p):
    """Make each word from paragraph a Word instance
    params: p   -   input paragraph of tagged text
    returns: list of Word instances
    """

    return [Word(w, i) for i, w in enumerate(p)]

def directCompare(eng, sp):
    """Pair up words translated to the same words in english
    params: eng -   list of word objects for english words
            sp  -   list of word objects from translated sp to eng
    returns: pairs  -   [matched word, index of matched word, translated match indices]
    """

    pairs = []
    for i, w1 in enumerate(eng):
        curr_indices = []
        for j, w2 in enumerate(sp):
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
    return BASE_URL + 'phrase1=' + w1 + '&' + 'phrase2=' + w2

def checkSynonmyms(eng_list, sp_list):
    """Checks for synonyms in two lists of word instances
    params: eng_list    -   list of word instances in english
            sp_list     -   list of word instances from translated spanish
    returns:
    """

    matches = []
    for i, w1 in enumerate(eng_list):
        base_pos = getPartsOfSpeech(w1)

        for j, w2 in enumerate(sp_list):
            sub_pos = getPartsOfSpeech(w2)

            # compare parts of speech
            same_pos = compareLists(base_pos, sub_pos)
            if same_pos:
                eng_pct = i / float(len(eng_list))
                sp_pct = j / float(len(sp_list))

                # compare relative positions in text
                if abs(eng_pct - sp_pct) < 0.20:
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

if __name__ == '__main__':
    main()
