from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import loader
import requests
import json
import pickle
from util import cosine_sim
import IPython as ipy

def clean_business_types():
  business_types_dict = loader.get_business_types()
  for k in business_types_dict.keys():
    if business_types_dict[k] is None:
      business_types_dict[k] = ''
    strs = business_types_dict[k].split(' ')
    s = []
    for st in strs:
      if st not in [None, 'agency','point_of_interest','establishment','sublocality','route','real','political','of','or','local','locality','intersection','1']:
        s += [st]
    if len(s) == 0:
      business_types_dict[k] = ''
    else:
      business_types_dict[k] = ' '.join(s)
  loader.dump_business_dict(business_types_dict)

if __name__ == '__main__':
  clean_business_types()