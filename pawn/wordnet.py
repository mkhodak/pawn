from collections import defaultdict
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Lemma
from nltk.corpus.reader.wordnet import Synset
from nltk.corpus.reader.wordnet import WordNetCorpusReader
from nltk.corpus.reader.wordnet import WordNetError
import pawn.load as data


_indicator = '_'
_dummy = 'DUMMY~'


###############################################################################
################ Synset Wrapper, Replacement, and Access Methods ##############
###############################################################################


# updates synset based on current language
def _synset_update(synset):
	language = data._language
	if dir(synset)[0] == _indicator:
		if synset._language != language:
			PWN_name = synset._PWN_name
			if language == 'en':
				setattr(synset, '_name', PWN_name)
			else:
				setattr(synset, '_name', data._synset2lang.get(PWN_name, _dummy+PWN_name))
			setattr(synset, '_language', language)
	else:
		PWN_name = synset._name
		setattr(synset, '_PWN_name', PWN_name)
		if language != 'en':
			setattr(synset, '_name', data._synset2lang.get(PWN_name, _dummy+PWN_name))
		setattr(synset, _indicator, None)
		setattr(synset, '_language', language)


# wrapper to update class 'Synset' before function execution
def _synset_wrapper(func, nargs):
	if nargs == 1:
		def wrapper(self):
			_synset_update(self)
			return func(self)
	elif nargs == 2:
		def wrapper(self, other):
			_synset_update(self)
			_synset_update(other)
			return func(self, other)
	return wrapper


def synset(name):
	"""emulates wn.synset"""
	if data._language != 'en':
		if name[:len(_dummy)] == _dummy:
			name = name[len(_dummy):]
		else:
			name = data._synset2pwn[name]
	return wn.synset(name)


def synsets(token, pos='anrsv'):
	"""emulates wn.synsets"""
	if data._language == 'en':
		return wn.synsets(name)
	return [wn.synset(name) for name in data._word2synsets[token] if name.split('.')[-2] in pos]


###############################################################################
################ Lemma Wrapper, Replacement, and Access Methods ###############
###############################################################################


# instantiation of Lemma object
def _lemma(name, synset):
	language = data._language
	synset_name = synset.name()
	for lemma_name, lemma in _lemmas[language][synset_name].items():
		if name == lemma_name:
			return lemma
	lemma = Lemma(WordNetCorpusReader, synset, name, 0, 0, None)
	_lemmas[language][synset_name][name] = lemma
	return lemma


# replacement for 'lemmas' method of class 'Synset'
def _synset_lemmas(self):
	if data._language == 'en':
		return self._lemmas
	return [_lemma(name, self) for name in data._synset2lemmas.get(self.name(), [])]


# replacement for 'lemma_names' method of class 'Synset'
def _synset_lemma_names(self):
	if data._language == 'en':
		return self._lemma_names
	return [name for name in data._synset2lemmas.get(self.name(), [])]


# wrapper for lexical relation functions of class 'Lemma'
def _lexical_relation_wrapper(func):
	def wrapper(self):
		if data._language == 'en':
			return func(self)
		return sum((lemma2.synset().lemmas() for lemma1 in wn.synset(self._PWN_name)._lemmas for lemma2 in func(lemma1)), [])
	return wrapper


# replacement for 'count' method of class 'Lemma'
def _lemma_count(self):
	if data._language == 'en':
		return self.count()
	return len(data._word2synsets[self._name])


def lemma(name):
	"""emulates wn.lemma"""
	if data._language == 'en':
		return wn.lemma(name)

	chunks = name.split('.')
	i = 3
	success = 0
	while not success:
		try:
			synsetname = '.'.join(chunks[:i])
			lemmas = data._synset2lemmas[synsetname]
			success = 1
		except KeyError:
			i += 1
	if name in lemmas:
		lemmaname = '.'.join(chunks[i:])
		return _lemma(lemmaname, synset(synsetname))
	raise WordNetError('Lemma ' + name + ' Not Found')


def lemmas(token, pos='anrsv'):
	"""emulates wn.lemmas"""
	if data._language == 'en':
		return wn.lemmas(token, pos)
	return [_lemma(token, wn.synset(name)) 
			for name in data._word2synsets[token] 
			if name.split('.')[-2] in pos]


###############################################################################
################ Initialization and Function Wrapping #########################
###############################################################################


def _wrap_class_method(Object, method, wrapper, *args):
	setattr(Object, method, wrapper(getattr(Object, method), *args))


def all_lemma_names():
	if data._language == 'en':
		return wn.all_lemma_names()
	return data._wordcounts.keys()


def all_synsets():
	if data._language == 'en':
		return wn.all_synsets()
	return (wn.synset(synset) for synset in data._synset2lemmas.keys())


_lemmas = defaultdict(lambda: defaultdict(lambda: {}))

_wrap_class_method(Synset, 'name', _synset_wrapper, 1)
_wrap_class_method(Synset, '__repr__', _synset_wrapper, 1)
_wrap_class_method(Synset, '__hash__', _synset_wrapper, 1)
_wrap_class_method(Synset, '__eq__', _synset_wrapper, 2)
_wrap_class_method(Synset, '__ne__', _synset_wrapper, 2)
_wrap_class_method(Synset, '__lt__', _synset_wrapper, 2)
setattr(Synset, 'lemmas', _synset_lemmas)
setattr(Synset, 'lemma_names', _synset_lemma_names)

_wrap_class_method(Lemma, 'antonyms', _lexical_relation_wrapper)
_wrap_class_method(Lemma, 'pertainyms', _lexical_relation_wrapper)
setattr(Lemma, 'count', _lemma_count)

lemma_count = lambda lemma: lemma.count()
words = all_lemma_names
wn.ensure_loaded()
for attr in dir(wn):
	if attr != '_' and not attr in globals():
		globals()[attr] = getattr(wn, attr)
