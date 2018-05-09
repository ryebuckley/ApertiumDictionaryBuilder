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

    for i in range(len(sp_trans_sents[0])):
        w = Word(sp_trans_sents[0][i], i)
    # compareParagraph(enwords, spwords)


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
        if '.<sent>' in phrase:
            if tmp:
                sents.append(tmp)
                tmp = []
        elif phrase:
            tmp.append(phrase)

    return sents









if __name__ == '__main__':
    main()
