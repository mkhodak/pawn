# Princeton Automated WordNet

The Princeton Automated WordNet (PAWN) is a multi-lingual (English-French-Russian) WordNet built by matching lemmas in French and Russian to existing synsets in the Princeton English WordNet (PWN) (https://wordnet.princeton.edu) using a word-vector approach paired with automated machine translation. The repository provides these word-synset matchings through a python API wrapping the Natural Language ToolKit (NLTK) WordNet Corpus that allows for accessing nodes in the WordNet graph by inputting words in any of the three languages. 

The API emulates that provided for PWN by NLTK. PWN synsets that do not have corresponding synsets in French or Russian are displayed as dummy synsets in those languages. The morphological root form of words is determined by TreeTagger lemmatization if its Python wrapper (treetaggerwrapper) is available; otherwise a rough heuristical morphology is used for French and an independent morphology analyzer (pymorphy2) is used for Russian. The module is implemented for Python 3.5.3 and depends on nltk, pymorphy2, and ujson.

This work is joint with Andrej Risteski, Christiane Fellbaum, and Sanjeev Arora.
