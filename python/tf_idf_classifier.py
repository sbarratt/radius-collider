import json
import util
import IPython as ipy
import bisect
from random import shuffle

#FIXME
"""
Traceback (most recent call last):
  File "tf_idf_classifier.py", line 29, in <module>
    business_desc = util.add_synonyms_to_text(business['description'])
  File "/Users/shane/Documents/ucb/_2015fa/radius-collider/python/util.py", line 47, in add_synonyms_to_text
    return ' '.join(add_synonyms(clean_paragraph(text)))
  File "/Users/shane/Documents/ucb/_2015fa/radius-collider/python/util.py", line 56, in clean_paragraph
    text.decode('utf-8')
  File "/Users/shane/anaconda/lib/python2.7/encodings/utf_8.py", line 16, in decode
    return codecs.utf_8_decode(input, errors, True)
UnicodeEncodeError: 'ascii' codec can't encode character u'\u201d' in position 81: ordinal not in range(128)
"""

ADD_SYNONYMS = True

with open('../challenge_set.json') as data_file:
  businesses = json.load(data_file)

with open('../naics_list.json') as data_file:
  naics = json.load(data_file)

shuffle(businesses)
for business in businesses:
  l = []
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
    sim = .3*t_t_sim+.4*d_t_sim+.1*t_d_sim+.1*d_d_sim
    # sim = .4*t_t_sim+.2*d_t_sim+.1*t_d_sim+.1*d_d_sim
    bisect.insort(l, (sim, naic))
  l = l[::-1]
  best_naic = l[0][1]
  print ""
  print business['name']
  print business['description']
  print "\nCLASSIFIED AS\n"
  print best_naic['title']
  print best_naic['description']
  print "Confidence:", l[0][0]
  print "------------------------------------"
