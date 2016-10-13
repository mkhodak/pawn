from collections import defaultdict
from functools import partial, wraps
try:
	import ujson as json
except ImportError:
	import json


_datapath = './pawn/data/'
_language = 'en'


# caching wrapper to store language dictionaries
def _language_cache(func, names):
	cache = {'en': {name: {} for name in names}}
	@wraps(func)
	def wrapper(*args, **kwargs):
		if _language in cache:
			for name in names:
				globals()[name] = cache[_language][name]
		else:
			func(*args, **kwargs)
			cache[_language] = {name: globals()[name] for name in names}
	return wrapper


# load word-synset matching data
@partial(_language_cache, names=['_word2synsets'])
def _load_word2synsets():
	global _word2synsets
	with open(_datapath+_language+'_data.json', 'r') as f:
		_word2synsets = json.load(f)


# load word count data
@partial(_language_cache, names=['_wordcounts'])
def _load_wordcounts():
	global _wordcounts
	with open(_datapath+_language+'_vocab.txt', 'r') as f:
		_wordcounts = {word: int(count) for word, count in (line.split() for line in f)}


# sets dictionaries for mapping synsets between languages and synsets to lemmas
@partial(_language_cache, names=['_synset2lemmas', '_synset2pwn', '_synset2lang'])
def _set_synsetmaps():
	global _synset2lemmas
	global _synset2pwn
	global _synset2lang
	synset2lemmas = defaultdict(lambda: [])
	for word, synsets in _word2synsets.items():
		for synset in synsets:
			synset2lemmas[synset].append(word)
	_synset2lemmas = {}
	_synset2pwn = {}
	_synset2lang = {}
	wordcounts = bool(_wordcounts)
	for synset, lemmas in sorted(synset2lemmas.items()):
		if wordcounts:
			sortedlemmas = sorted(lemmas, key=_wordcounts.__getitem__, reverse=True)
		else:
			sortedlemmas = sorted(lemmas)
		name = '.'.join([sortedlemmas[0], synset.split('.')[-2], '01'])
		index = 1
		while name in _synset2pwn:
			index += 1
			name[-2:] = (index<10)*'0'+str(index)
		_synset2pwn[name] = synset
		_synset2lang[synset] = name
		_synset2lemmas[name] = ['.'.join([name, lemma]) for lemma in sortedlemmas]


# reload and reset all dictionaries
def _reset():
	_load_word2synsets()
	_load_wordcounts()
	_set_synsetmaps()


def language():
	"""get current language setting"""
	return _language


def set_language(language):
	"""reset language setting"""
	global _language
	if _language != language:
		_language = language
		_reset()
