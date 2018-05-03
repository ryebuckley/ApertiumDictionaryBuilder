from subprocess import *
def main():

    p1 = Popen(["cat", "corpora/littleredridinghood.es"], stdout=PIPE)
    p2 = Popen(["apertium", "-d", "developed_resources/apertium-en-es/", "es-en-postchunk"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output=p2.communicate()[0]
    output = output.decode()
    output = output.split("^")
    print(output[3])

    p1 = Popen(["cat", "corpora/littleredridinghood.en"], stdout=PIPE)
    p2 = Popen(["apertium", "-d", "developed_resources/apertium-eng/", "eng-tagger"], stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output1=p2.communicate()[0]
    output1 = output1.decode()
    output1 = output1.split("^")
    print(output1[3])

    output, output1 = organize(output, output1)
    write_to_file(output, output1)

def organize(t1, t2):
    """
        try and line words up correctly
    """
    
    return t1, t2

def write_to_file(t1, t2):
    """
        write two lists to a file matching items
    """
    f = open("test.txt", "w")
    for i in range(20):
        f.write(t1[i])
        f.write("\n")
        f.write(t2[i])
        f.write("\n")
        f.write("\n")

    f.close()

main()
