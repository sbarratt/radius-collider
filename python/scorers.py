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
  def __init__(self, weights = [.2,.5,.1,.3]):
    self.google_types = loader.get_business_types()
    self.weights = weights

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
      business_name = util.add_synonyms_to_text(business_name)

    for naic in naics:
      naic_desc = naic['description']
      naic_title = naic['title']
      if ADD_SYNONYMS:
        naic_title = util.add_synonyms_to_text(naic_title)
        naic_desc = util.add_synonyms_to_text(naic_desc)

      d_d_sim = util.cosine_sim(business_desc, naic_desc)
      t_t_sim = util.cosine_sim(business['name'], naic['title'])
      d_t_sim = util.cosine_sim(business_desc, naic_title)
      t_d_sim = util.cosine_sim(business_name, naic_desc)
      sim = util.dotproduct(self.weights, [d_d_sim, t_t_sim, d_t_sim, t_d_sim])
      bisect.insort(l, (sim, naic))
    l = l[::-1]
    return l