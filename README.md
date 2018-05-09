# ApertiumDictionaryBuilder
Contains a tool to add dictionary entries into a machine translation system
between two languages with well developed transducers by scanning two parallel
corpora 

The lexL and lexR input files.
These files should be txt files containing which tags are
lexical tags in each language. The lexL file should contain the information for
the language on the left side of the dictionary entry and the lexR file should
contain the information for the langauge on the right side of the dictionary
entries.
These files should be formated such that there is one tag per line, with no
extra punctuation or symbols. Triangle brackets or any other special symbols
often around tags should also be left off such that only letters are included.
For example:
n
adj
vblex
f
nt
<!-- end example -->
There are two input files, one for the left language and one for the right
language in case a certain tag is lexical in one language but morphological in
the other. You may pass in the same txt file for both input files if this is not
 the case for your language pair.


Some notes on where in your dictionary file our tool will insert new entries:
If there are already existing entries in your dictionary with the same part of
speech as the new entry our tool has generated, our tool will add the new entry
the line above the first instance of an existing entry with that part of speech.
If the new entry is to be the first entry with it's part of speech our tool will
 add the new entry on the very last line of the dictionary entry section of your
 dictionary file. Our tool will recognize the end of the dictionary entry
section by the closing tag </section>.
