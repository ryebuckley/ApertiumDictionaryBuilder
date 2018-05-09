from subprocess import *

OUTFILE = "tranlsation.txt"

def main():
    d = readData(
        'corpora/littleredridinghood.es',
        '../apertium/apertium-en-es/',
        'es-en-postchunk'
    )

    lines = []
    for wd in d:
        if '<' in wd:
            idx = wd.index('<')
            lines.append(wd[:idx])
        else:
            lines.append(wd)

    with open(OUTFILE, 'w') as f:
        for line in lines:
            f.write(line)
            f.write(' ')


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



main()
