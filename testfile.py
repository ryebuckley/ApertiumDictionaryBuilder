from subprocess import *

# subprocess.run(["echo", "'bird'", "|", "apertium", "-d", "developed_resources/apertium-en-es/", "en-es"])
# subprocess.run(["echo", "'bird' | apertium -d developed_resources/apertium-en-es/ en-es"])
# subprocess.run(["ls", "-l"])
p1 = Popen(["echo", "bird"], stdout=PIPE)
p2 = Popen(["apertium", "-d", "developed_resources/apertium-en-es/", "en-es"], stdin=p1.stdout, stdout=PIPE)
p1.stdout.close()
output=p2.communicate()[0]
print(output.decode())


p1 = Popen(["cat", "corpora/littleredridinghood.eng"], stdout=PIPE)
p2 = Popen(["apertium", "-d", "developed_resources/apertium-en-es/", "en-es-tagger"], stdin=p1.stdout, stdout=PIPE)
p1.stdout.close()
output=p2.communicate()[0]
print(output.decode())
