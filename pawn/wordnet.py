from collections import defaultdict
from functools import wraps
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Lemma
from nltk.corpus.reader.wordnet import Synset
from nltk.corpus.reader.wordnet import WordNetCorpusReader
from nltk.corpus.reader.wordnet import WordNetError
import pawn.load as data


_indicator = '_'
_dummy = 'DUMMY~'


# wrapper that returns PWN function output if current language is English
def _english_wrapper(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if data._language == 'en':
			wn.ensure_loaded()
			return getattr(wn, func.__name__)(*args, **kwargs)
		return func(*args, **kwargs)
	return wrapper


@_english_wrapper
def morphy(token):
	"""emulates wn.morphy"""
	if token in data._word2synsets:
		return token
	if ' ' in token:
		return None
	morph = data._morphy(token)
	if morph in data._word2synsets:
		return morph
	return None


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


@_english_wrapper
def synsets(token, pos='anrsv'):
	"""emulates wn.synsets"""
	morph = morphy(token)
	if morph:
		return [wn.synset(name) for name in data._word2synsets[morph] if name.split('.')[-2] in pos]
	return []


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


@_english_wrapper
def lemma(name):
	"""emulates wn.lemma"""
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


@_english_wrapper
def lemmas(token, pos='anrsv'):
	"""emulates wn.lemmas"""
	morph = morph(token)
	if morph:
		return [_lemma(token, wn.synset(name)) for name in data._word2synsets[morph] if name.split('.')[-2] in pos]
	return []


###############################################################################
################ Initialization and Function Wrapping #########################
###############################################################################


# function to wrap a method of given object with a given wrapper
def _wrap_class_method(Object, method, wrapper, *args):
	setattr(Object, method, wrapper(getattr(Object, method), *args))


# ensures corpus has been loaded before returning function
def _lazy_function(name):
	def function(*args, **kwargs):
		wn.ensure_loaded()
		return getattr(wn, name)(*args, **kwargs)
	return function


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

globals()['abspath'] = _lazy_function('abspath')
globals()['abspaths'] = _lazy_function('abspaths')
all_lemma_names = _english_wrapper(lambda: data._wordcounts.keys())
all_synsets = _english_wrapper(lambda: (wn.synset(synset) for synset in data._synset2lemmas.keys()))
globals()['citation'] = _lazy_function('citation')
globals()['encoding'] = _lazy_function('encoding')
globals()['fileids'] = _lazy_function('fileids')
globals()['get_version'] = _lazy_function('get_version')
globals()['ic'] = _lazy_function('ic')
globals()['jcn_similarity'] = _lazy_function('jcn_similarity')
globals()['langs'] = _lazy_function('langs')
globals()['lch_similarity'] = _lazy_function('lch_similarity')
lemma_count = lambda lemma: lemma.count()
globals()['lemma_from_key'] = _lazy_function('lemma_from_key')
globals()['license'] = _lazy_function('license')
globals()['lin_similarity'] = _lazy_function('lin_similarity')
globals()['of2ss'] = _lazy_function('of2ss')
globals()['open'] = _lazy_function('open')
globals()['path_similarity'] = _lazy_function('path_similarity')
globals()['readme'] = _lazy_function('readme')
globals()['res_similarity'] = _lazy_function('res_similarity')
globals()['root'] = _lazy_function('root')
globals()['ss2of'] = _lazy_function('ss2of')
globals()['unicode_repr'] = _lazy_function('unicode_repr')
words = all_lemma_names
globals()['wup_similarity'] = _lazy_function('wup_similarity')
