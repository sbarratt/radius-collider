import bisect
import IPython as ipy
import util
import loader


WIEGHTS_DICT = {
   'd_d_sim': .2,
   't_t_sim': .5,
   'd_t_sim': .1,
   't_d_sim': .3
}

class TfidfScorer:
  google_types = loader.get_business_types()

  def __init__(self, weights_dict = WIEGHTS_DICT):
    self.weights_dict = weights_dict

  @staticmethod
  def get_features(business, naics, ADD_SYNONYMS=False):
    business_desc = business['description']
    google_type = TfidfScorer.google_types.get(business['unique_id'])
    if google_type is not None:
      business_name = google_type
    else:
      business_name = ''

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

      d_d_sim = util.cosine_sim(business_desc, naic_desc)
      t_t_sim = util.cosine_sim(business['name'], naic['title'])
      d_t_sim = util.cosine_sim(business_desc, naic_title)
      t_d_sim = util.cosine_sim(business_name, naic_desc)
      features = {
         'd_d_sim': d_d_sim,
         't_t_sim': t_t_sim,
         'd_t_sim': d_t_sim,
         't_d_sim': t_d_sim
      }
      codes_to_features[naic['code']] = features
    return codes_to_features

  def score_business(self, business_from_db):
    l = []
    for naics_code, features in business_from_db.getFeatureDict().iteritems():
      sim = 0
      sim += self.weights_dict['d_d_sim']*features['d_d_sim']
      sim += self.weights_dict['t_t_sim']*features['t_t_sim']
      sim += self.weights_dict['d_t_sim']*features['d_t_sim']
      sim += self.weights_dict['t_d_sim']*features['t_d_sim']
      bisect.insort(l, (sim, naics_code))
    l = l[::-1]
    return l
