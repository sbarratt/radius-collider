from nltk.corpus import wordnet as wn

def add_synonyms(words):
  more_words = []
  for word in words:
    nltk_id = word + '.n.01'
    more_words += wn.synset(nltk_id).lemma_names()
  return more_words

