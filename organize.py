import os
from subprocess import *

from word import Word
from entry import Entry

ENGLISH_TEXT = 'corpora/test.en' # "corpora/littleredridinghood.en"
SPANISH_TEXT = 'corpora/test.sp' # "corpora/littleredridinghood.es"
EN_ES_PATH = "../apertium/apertium-en-es/"
EN_PATH = "../apertium/apertium-eng/"

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

    ### now tag comparison phase

    



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

    for e in matched:
        for pair in e.matches:
            print "Matched (%s, %s) at indices (%d, %d)" % (
            e.word, e.word, pair[0], pair[1]
        )

    pct = float(len(matched)) / len(wd_ls)
    print "Percentage matched: %.3f" % pct

def reduceParagraph(used_words, word_ls):
    """Take out already matched words from list of word instances
    params: used_words  -   list of words that have already been matched
            word_ls     -   list of word instances
    returns: list of unmatched words
    """

    return [wd for wd in word_ls if wd.word not in used_words]

if __name__ == '__main__':
    main()
