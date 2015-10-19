from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim.models import word2vec
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import bisect
import IPython as ipy
import util
import loader

class TfidfScorer:
  def __init__(self, weights = [.2,.5,.1,.3,.1,.5,.1,.1]):
    self.google_types = loader.get_business_types()
    self.weights = weights
    self.model = loader.get_word2vecmodel()

  def word2vec_sim(self, text1, text2):
    w1 = filter(lambda x: x in self.model.vocab, util.clean_paragraph(text1))
    w2 = filter(lambda x: x in self.model.vocab, util.clean_paragraph(text2))
    sim = self.model.n_similarity(w1,w2)
    return sim

  def score_business(self, business, naics, ADD_SYNONYMS=False):
    l = []
    business_desc = business['description']
    google_type = self.google_types.get(business['unique_id'])
    if google_type is not None:
      business_name = google_type
    else:
      business_name = ''

    if ADD_SYNONYMS:
      business_desc = util.add_synonyms_to_text(business_desc)
      # business_name = util.add_synonyms_to_text(business_name)

    for naic in naics:
      naic_desc = naic['description']
      naic_title = naic['title']
      if ADD_SYNONYMS:
        naic_title = util.add_synonyms_to_text(naic_title)
        naic_desc = util.add_synonyms_to_text(naic_desc)

      d_d_cosine_sim = util.cosine_sim(business_desc, naic_desc)
      t_t_cosine_sim = util.cosine_sim(business_name, naic_title)
      d_t_cosine_sim = util.cosine_sim(business_desc, naic_title)
      t_d_cosine_sim = util.cosine_sim(business_name, naic_desc)

      d_d_word2vec_sim = self.word2vec_sim(business_desc, naic_desc)
      t_t_word2vec_sim = self.word2vec_sim(business_name, naic_title)
      d_t_word2vec_sim = self.word2vec_sim(business_desc, naic_title)
      t_d_word2vec_sim = self.word2vec_sim(business_name, naic_desc)

      feats = [d_d_cosine_sim, t_t_cosine_sim, d_t_cosine_sim, t_d_cosine_sim, d_d_word2vec_sim, t_t_word2vec_sim, d_t_word2vec_sim, t_d_word2vec_sim]

      sim = util.dotproduct(self.weights, feats)

      bisect.insort(l, (sim, naic))
    l = l[::-1] #reverse
    return l