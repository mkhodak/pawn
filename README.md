# Princeton Automated WordNet

This repository is a Python package wrapping the Princeton English WordNet (PWN) (https://wordnet.princeton.edu) in order to link it to automatically-constructed French and Russian WordNets, which were constructed via a word-vector approach supported by automated machine translation. It is based on joint work with Andrej Risteski, Christiane Fellbaum, and Sanjeev Arora.

The API emulates that provided for PWN by the Natural Language ToolKit (NLTK). PWN synsets that do not have corresponding synsets in French or Russian are displayed as dummy synsets in those languages. The morphological root form of words is determined by TreeTagger if its Python wrapper (treetaggerwrapper) is available; otherwise a heuristical stemmer is used for French and a morphology analyzer (pymorphy2) is used for Russian.
