from subprocess import *
import urllib2
import os

from word import Word
from entry import Entry

ENGLISH_TEXT = "corpora/littleredridinghood.en" # 'corpora/test.en'
SPANISH_TEXT = "corpora/littleredridinghood.es" # 'corpora/test.sp'
EN_ES_PATH = "../apertium/apertium-en-es/"
EN_PATH = "../apertium/apertium-eng/"
BASE_URL = "http://swoogle.umbc.edu/SimService/GetSimilarity?operation=api&"

DEFAULT_THRESH = 0.2
THRESH_DICT = {
    'vblex': 0.7,
    'vbmod': 0.7,
}

def main():

    eng = readData(ENGLISH_TEXT, EN_PATH, "eng-tagger")
    sp_trans = readData(SPANISH_TEXT, EN_ES_PATH, "es-en-postchunk")

    eng_sents = getSentences(eng)
    sp_trans_sents = getSentences(sp_trans)

    assert(len(eng_sents) == len(sp_trans_sents))

    eng_reduced, sp_reduced = [], []
    for i in range(len(eng_sents)):
        eng, sp = eng_sents[i], sp_trans_sents[i]
        entries, eng_words, sp_words = compareParagraph(eng, sp)
        used_words = [w.word for w in entries]

        evalCoverage(eng, entries)
        eng_red = reduceParagraph(used_words, eng_words)
        sp_red = reduceParagraph(used_words, sp_words)

        eng_reduced.append(eng_red)
        sp_reduced.append(sp_red)
        break

    ### now tag comparison phase

    matches = checkSynonmyms(eng_red, sp_red)




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

def evalCoverage(wd_ls, matched):
    """Evaluate how well matching did
    params: wd_ls   -   all words in corpus
            matched -   number of matches
    returns: nothing; prints statistic
    """

    # for e in matched:
    #     for pair in e.matches:
    #         print "Matched (%s, %s) at indices (%d, %d)" % (
    #         e.word, e.word, pair[0], pair[1]
    #     )

    match_count = sum([w.getNumMatches() for w in matched])
    pct = float(match_count) / len(wd_ls)
    print "Percentage matched: %.3f" % pct

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
                    page = urllib2.urlopen(createURL(w1, w2))
                    score = float(page.read())

                    # check if score is above threshold
                    if score > THRESH_DICT.get(same_pos[0], DEFAULT_THRESH):
                        matches.append((w1, w2, score, i, j))

    return matches


def getPartsOfSpeech(w):

    return [ls[0] for ls in w.analyses if ls]

def compareLists(ls1, ls2):

    matches = []
    for item in ls1:
        if item in ls2:
            matches.append(item)
    return matches

if __name__ == '__main__':
    main()
