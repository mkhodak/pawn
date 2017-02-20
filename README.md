# Princeton Automated WordNet (PAWN)

The Princeton Automated WordNet (PAWN) is a multi-lingual (English-French-Russian) WordNet built by matching lemmas in French and Russian to existing synsets in the Princeton English WordNet (PWN) (https://wordnet.princeton.edu) using a word-vector approach paired with automated machine translation. The repository provides these word-synset matchings through a python API wrapping the Natural Language ToolKit (NLTK) WordNet Corpus that allows for accessing nodes in the WordNet graph by inputting words in any of the three languages. 

The API emulates that provided for PWN by NLTK. PWN synsets that do not have corresponding synsets in French or Russian are displayed as dummy synsets in those languages. The morphological root form of words is determined by TreeTagger lemmatization if its Python wrapper (treetaggerwrapper) is available; otherwise a rough heuristical morphology is used for French and an independent morphology analyzer (pymorphy2) is used for Russian. The module is implemented for Python 3.5.3 and depends on nltk, pymorphy2, and ujson.

This work is joint with Andrej Risteski, Christiane Fellbaum, and Sanjeev Arora (http://unsupervised.cs.princeton.edu).

# Test Sets for Automated WordNet Construction

In testset.zip we provide word-to-synset matching test sets for evaluating WordNets in French and Russian.

French: fr_matches.txt
Russian: ru_matches.txt

Each file has binary 0-1 labeled candidate synsets for 200 adjectives, 200 nouns, and 200 verbs in the form:

INDEX	TARGET_WORD
LABEL	CANDIDATE_SYNSET	SYNSET_DESCRIPTION  
.  
.  
.  
LABEL	CANDIDATE_SYNSET	SYNSET_DESCRIPTION

# Citation

If you use the provided code or test set in academic work, please cite the following:

@inproceedings{PAWN:17,  
	author={Mikhail Khodak and Andrej Risteski and Christiane Fellbaum and Sanjeev Arora},  
	title={Automated WordNet Construction Using Word Embeddings},  
	booktitle={EACL 2017 Workshop on Sense, Concept, and Entity Representations and their Applications},  
	year=2017,  
	note={To Appear}  	
}
