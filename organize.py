import os
from subprocess import *

from word import Word


ENGLISH_TEXT = "corpora/littleredridinghood.en"
SPANISH_TEXT = "corpora/littleredridinghood.es"
EN_ES_PATH = "../apertium/apertium-en-es/"
EN_PATH = "../apertium/apertium-eng/"

def main():

    eng = readData(ENGLISH_TEXT, EN_PATH, "eng-tagger")
    sp_trans = readData(SPANISH_TEXT, EN_ES_PATH, "es-en-postchunk")

    eng_sents = getSentences(eng)
    sp_trans_sents = getSentences(sp_trans)

    assert(len(eng_sents) == len(sp_trans_sents))

    for i in range(len(eng_sents)):
        eng, sp = eng_sents[i], sp_trans_sents[i]
        compareParagraph(eng, sp)
        break


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
    for phrase in text:
        if '\n\n' in phrase:
            if tmp:
                sents.append(tmp)
                tmp = []
        elif phrase:
            tmp.append(phrase)

    return sents

def compareParagraph(eng, sp):

    eng_words = translateParagraph(eng)
    sp_words = translateParagraph(sp)
    pairs = directCompare(eng_words, sp_words)

    seen_words = []
    # for

def translateParagraph(p):
    """Make each word from paragraph a Word instance
    params: p   -   input paragraph of tagged text
    returns: list of Word instances
    """

    return [Word(w, i) for i, w in enumerate(p)]

def directCompare(eng, sp):

    pairs = []
    for i, w1 in enumerate(eng):
        curr_indices = []
        for j, w2 in enumerate(sp):
            if w1.word == w2.word:
                curr_indices.append(j)

        if curr_indices:
            pairs.append([w1.word, i, curr_indices])

    return pairs



if __name__ == '__main__':
    main()
