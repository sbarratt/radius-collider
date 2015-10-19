"""
python/get_business_types.py

Script to get businesses types from their lat lon
"""
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import loader
import requests
import json
import pickle
from util import cosine_sim
import IPython as ipy

# API_KEY = "AIzaSyDEVQJmING4SQSZbcap0YYV6Dt4dFt78tY" #Myles
# API_KEY = 'AIzaSyCdVPTYLYttmFGw7wVxNewCFV-DFSuUcBw' #Shane - don't use it too much it will charge my credit card
API_KEY = "AIzaSyAKVlnW6xrtTdHtwnE1R2x-2ewJQb-ACCM" #Shane
# API_KEY = "AIzaSyC43m3xgSQtkbFzQ5Oa8XMH3Gq49RCR3oU" #Alex

def url(code):
  return "http://api.naics.us/v0/q?year=2012&code={}".format(code)

def get_places(lat, lng):
  # uri = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&radius=500&key=%s' % (address, API_KEY)
  uri = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=50&key=%s' % (lat, lng, API_KEY)
  resp = json.loads(requests.get(uri).content)
  if resp['status'] == 'OVER_QUERY_LIMIT':
    raise Exception('over query limit')
  return resp['results']

def get_all_business_types():
  businesses = loader.get_challengeset()
  idtoloc = loader.get_idtoloc()
  business_types_dict = loader.get_business_types()
  print len(business_types_dict)
  for business in businesses:
    unique_id = business['unique_id']
    # if unique_id not in business_types_dict.keys():
    if business_types_dict.get(unique_id) is None:
      print business['name']
      closest_place, best_sim = None, 0
      lat, lon = idtoloc[unique_id]
      for place in get_places(lat, lon):
        sim = cosine_sim(place['name'], business['name'])
        if sim > best_sim:
          closest_place = place
          best_sim = sim
      if closest_place:
        types = filter(lambda x: not x in ['point_of_interest','establishment','sublocality','route','real','political','of','or','local','locality','intersection','1'], closest_place['types'])
        types = " ".join(types).replace("_"," ")
      else:
        types = None
      print types
      business_types_dict[unique_id] = types
      loader.dump_business_dict(business_types_dict)

def clean_business_types():
  business_types_dict = loader.get_business_types()
  for k in business_types_dict.keys():
    strs = business_types_dict[k].split(' ')
    s = []
    for st in strs:
      if st not in [None, 'health','point_of_interest','establishment','sublocality','route','real','political','of','or','local','locality','intersection','1']:
        s += [st]
    if len(s) == 0:
      business_types_dict[k] = ''
    else:
      business_types_dict[k] = ' '.join(s)
  loader.dump_business_dict(business_types_dict)

if __name__ == '__main__':
  get_all_business_types()
  # clean_business_types()