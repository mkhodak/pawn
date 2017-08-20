from collections import defaultdict
from functools import wraps
from operator import itemgetter
from nltk.corpus.reader.wordnet import WordNetError
import pymorphy2


_langmap = {'fr': 'french', 'ru': 'russian'}
_underscore2space = str.maketrans('_', ' ')
_french_morphology = defaultdict(lambda: {})
for suffix in ['ons', 'ez', 'ent', 'ais', 'ait', 'ions', 'iez', 'aient', 'ai', 'ont', 'eons', 'é', 'és', 'ée']:
  _french_morphology[len(suffix)][suffix] = 'er'
for suffix in ['ssons', 'ssez', 'ssent']:
  _french_morphology[len(suffix)][suffix] = 'ir'
for suffix in ['s', 'e', 'es']:
  _french_morphology[len(suffix)][suffix] = ''
for char in ['l', 'n', 's']:
  _french_morphology[3][2*char+'e'] = char
_french_morphology[4]['eaux'] = 'eau'
_max = max(_french_morphology.keys())
_morph = pymorphy2.MorphAnalyzer()
_methods = {'<FakeDictionary>', '<HyphenatedWordsAnalyzer>', '<PunctuationAnalyzer>', '<UnknAnalyzer>', '<UnknownSuffixAnalyzer>'}


# wrapper to split input and join output by underscore
def _stringsplit_wrapper(func):
  @wraps(func)
  def wrapper(string):
    return '_'.join(func(chunk) for chunk in string.split('_'))
  return wrapper


# tries to find root form of French word
@_stringsplit_wrapper
def _fr_morphy(string):
  for length in reversed(range(1, min(len(string)-1, _max))):
    suffix = _french_morphology[length].get(string[-length], None)
    if suffix != None:
      return string[:-length] + suffix
  return string


# tries to find root form of Russian word
@_stringsplit_wrapper
def _ru_morphy(string):
  scores = defaultdict(lambda: 0)
  for form in _morph.parse(string):
    if not _methods.intersection(str(method[0]) for method in form.methods_stack):
      score = form.score
      normal_form = form.normal_form
      if score >= .5:
        return normal_form
      scores[normal_form] += score
      if scores[normal_form] >= .5:
        return normal_form
  if scores:
    return max(scores.items(), key=itemgetter(1))[0]
  return string


class Morphy:


  # tries to find root form of word using TreeTagger lemmatizer
  def _treetagger_morphy(self, string):
    return '_'.join(tag.split('\t')[-1].lower() for tag in self._tagger.tag_text(string.translate(_underscore2space)))

  # tries to find root form of word using Snowball Stemmer
  @_stringsplit_wrapper
  def _snowball_morphy(self, string):
    stemmer = self._stemmer
    return '_'.join(stemmer.stem(token) for token in string.split())

  # sets TreeTagger as the morphology analyzer
  def _set_treetagger(self, language):
    import treetaggerwrapper as ttw
    try:
      self._tagger = ttw.TreeTagger(TAGLANG=language)
      self.morphy = self._treetagger_morphy
    except ttw.TreeTaggerError:
      raise(ImportError)

  # sets SnowballStemmer as the morphology analyzer
  def _set_snowball(self, language):
    from nltk.stem import SnowballStemmer
    self._stemmer = SnowballStemmer(_langmap[language])
    self.morphy = self._snowball_morphy

  # sets custom morphology analyzer
  def _set_morphy(self, language):
    try:
      self.morphy = globals()['_'+language+'_morphy']
    except KeyError:
      raise WordNetError('no custom morphology analyzer for ' + language + ' avaialable')


  # determines which language and morphological analyzer to use
  def __init__(self, language, analyzer):

    if analyzer == 'auto':
      try:
        self._set_treetagger(language)
      except ImportError:
        self._set_morphy(language)
    else:
      try:
        getattr(self, '_set_'+analyzer)(language)
      except AttributeError:
        raise WordNetError('no morphology analyzer ' + analyzer + 'available')
