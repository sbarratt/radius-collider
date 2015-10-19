import bisect
import IPython as ipy
import util
import loader
import numpy as np

WIEGHTS_DICT = {
   'd_d_sim': .1,
   't_t_sim': .2,
   'd_t_sim': .1,
   't_d_sim': .1,
   't_t_w2vsim': .5,
   'd_d_w2vsim': .2,
   'd_t_w2vsim': .2,
   't_d_w2vsim': .2
}

class TfidfScorer:
  google_types = loader.get_business_types()
  model = loader.get_word2vecmodel()

  def __init__(self, weights_dict = WIEGHTS_DICT):
    self.weights_dict = weights_dict

  @staticmethod
  def word2vec_sim(text1, text2):
    w1 = filter(lambda x: x in TfidfScorer.model.vocab, util.clean_paragraph(text1))
    w2 = filter(lambda x: x in TfidfScorer.model.vocab, util.clean_paragraph(text2))
    if w1 is None:
      w1 = []
    if w2 is None:
      w2 = []
    sim = TfidfScorer.model.n_similarity(w1, w2)
    return sim

  @staticmethod
  def get_features(business, naics, ADD_SYNONYMS=False):
    business_desc = business['description']
    google_type = TfidfScorer.google_types.get(business['unique_id'])
    business_name = google_type if google_type else ''
    business_name += ' ' + business['name']

    if ADD_SYNONYMS:
      business_desc = util.add_synonyms_to_text(business_desc)
      business_name = util.add_synonyms_to_text(business_name)

    codes_to_features = {}
    for naic in naics:
      naic_desc = naic['description']
      naic_title = naic['title']
      if ADD_SYNONYMS:
        naic_title = util.add_synonyms_to_text(naic_title)
        naic_desc = util.add_synonyms_to_text(naic_desc)

      business_name = str(business_name)
      business_desc = str(business_desc)
      naic_title = str(naic_title)
      naic_desc = str(naic_desc)

      d_d_sim = util.cosine_sim(business_desc, naic_desc)
      t_t_sim = util.cosine_sim(business_name, naic_title)
      d_t_sim = util.cosine_sim(business_desc, naic_title)
      t_d_sim = util.cosine_sim(business_name, naic_desc)

      t_t_w2vsim = TfidfScorer.word2vec_sim(business_name, naic_title)
      d_d_w2vsim = TfidfScorer.word2vec_sim(business_desc, naic_desc)
      d_t_w2vsim = TfidfScorer.word2vec_sim(business_desc, naic_title)
      t_d_w2vsim = TfidfScorer.word2vec_sim(business_name, naic_desc)

      if type(t_t_w2vsim) is not np.float64 or np.isnan(t_t_w2vsim):
        t_t_w2vsim = 0.0
      t_t_w2vsim = float(t_t_w2vsim)

      if type(d_d_w2vsim) is not np.float64 or np.isnan(d_d_w2vsim):
        d_d_w2vsim = 0.0
      d_d_w2vsim = float(d_d_w2vsim)

      if type(d_t_w2vsim) is not np.float64 or np.isnan(d_t_w2vsim):
        d_t_w2vsim = 0.0
      d_t_w2vsim = float(d_t_w2vsim)

      if type(t_d_w2vsim) is not np.float64 or np.isnan(t_d_w2vsim):
        t_d_w2vsim = 0.0
      t_d_w2vsim = float(t_d_w2vsim)

      features = {
          'd_d_sim': d_d_sim,
          't_t_sim': t_t_sim,
          'd_t_sim': d_t_sim,
          't_d_sim': t_d_sim,
          't_t_w2vsim': t_t_w2vsim,
          'd_d_w2vsim': d_d_w2vsim,
          'd_t_w2vsim': d_t_w2vsim,
          't_d_w2vsim': t_d_w2vsim
      }
      codes_to_features[naic['code']] = features
    return codes_to_features

  def score_business(self, business_from_db):
    l = []
    for naics_code, features in business_from_db.getFeatureDict().iteritems():
      sim = 0
      for k in features.keys():
        sim += self.weights_dict[k]*features[k]
      bisect.insort(l, (sim, naics_code))
    l = l[::-1]
    return l
