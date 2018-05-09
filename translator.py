from subprocess import *
import optparse
#-s corpora/littleredridinghood.es -e corpora/littleredridinghood.en
def main():

    parser = optparse.OptionParser(description="dissimilarity map builder")

    parser.add_option('-s', '--spanish', type='string', help='The name of a file storing spanish corpus')

    parser.add_option('-e', '--english', type='string', help='the name of a file storing an english corpus')

    parser.add_option('-o', '--output', type='string', help='the name of an output file')

    (opts, args) = parser.parse_args()

    mandatories = ["spanish", "english", "output"]

    for m in mandatories:
        if not opts.__dict__[m]:
            print('mandatory option ' + m + ' is missing\n')
            parser.print_help()
            sys.exit()


    p1 = Popen(["cat", opts.spanish], stdout=PIPE)
    p2 = Popen(["apertium", "-d", "developed_resources/apertium-en-es/", "es-en-postchunk"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output=p2.communicate()[0]
    output = output.decode()
    output = output.split("^")
    print(output[3])

    p1 = Popen(["cat", opts.english], stdout=PIPE)
    p2 = Popen(["apertium", "-d", "developed_resources/apertium-eng", "eng-tagger"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output1=p2.communicate()[0]
    output1 = output1.decode()
    output1 = output1.split("^")
    print(output1[3])

    output, output1 = organize(output, output1)
    write_to_file(output, output1, opts.output)

def organize(t1, t2):
    """
        try and line words up correctly
    """

    return t1, t2

def write_to_file(t1, t2, filename):
    """
        write two lists to a file matching items
    """
    f = open(filename, "w")
    for i in range(20):
        f.write(t1[i])
        f.write("\n")
        f.write(t2[i])
        f.write("\n")
        f.write("\n")

    f.close()

main()
