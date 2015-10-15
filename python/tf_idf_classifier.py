import json
import util
import IPython as ipy
from random import shuffle

# TODO decide when to not classify
# TODO translate ones in spanish

ADD_SYNONYMS = False

with open('../challenge_set.json') as data_file:
  businesses = json.load(data_file)

with open('../naics_list.json') as data_file:
  naics = json.load(data_file)

# Weigh title more than description
# frequency weighting
shuffle(businesses)
for business in businesses:
  best_sim = 0.0
  best_naic = 0
  for naic in naics:
    if ADD_SYNONYMS:
      business_desc = util.add_synonyms_to_text(business['description'])
      business_name = util.add_synonyms_to_text(business['name'])
      naic_title = util.add_synonyms_to_text(naic['title'])
      naic_desc = util.add_synonyms_to_text(naic['description'])
    else:
      business_desc = business['description']
      business_name = business['name']
      naic_desc = naic['description']
      naic_title = naic['title']
    d_d_sim = util.cosine_sim(business_desc, naic_desc)
    t_t_sim = util.cosine_sim(business['name'], naic['title'])
    d_t_sim = util.cosine_sim(business_desc, naic_title)
    t_d_sim = util.cosine_sim(business_name, naic_desc)
    sim = .1*t_t_sim+.4*d_t_sim+.1*t_d_sim+.3*d_d_sim
    # sim = .4*t_t_sim+.2*d_t_sim+.1*t_d_sim+.1*d_d_sim
    if sim > best_sim:
      best_naic = naic
      best_sim = sim
  print business['name']
  print business['description']
  print "\nCLASSIFIED AS"
  print best_naic['title']
  print best_naic['description']
  ipy.embed()