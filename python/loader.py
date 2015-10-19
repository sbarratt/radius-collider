import json, csv, pickle
import IPython as ipy
import os
from gensim.models import word2vec

DATA_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/data/"

def get_idtoloc():
  """ Returns dict: unique_id --> (lat, lng)
  If (None, None): geocode did not return a latitude/longitude

  Response Format:
  {
  u'1fe9adec-46f3-48f8-9fdd-4b715115a091': (38.3401715, -85.6214021),
  u'1fee61a2-571d-4789-ac98-3d670bc9acb3': (39.871075, -84.889905),
  u'1fee61a2-571d-4789-ac98-3d670bc9acb3': (None, None),
  ...
  u'2002c9ca-45a5-49a1-921b-191b2760c89f': (35.3930786, -119.120998),
  }
  """
  return pickle.load(open(DATA_DIR+'id_to_loc.pickle','r'))

def get_naicslist():
  """ Returns list of json naics objects

  Response Format:
  [
  {
    "code": 928120,
    "description": "This industry comprises establishments of U.S. and foreign governments primarily engaged in international affairs and programs relating to other nations and peoples.",
    "title": "International Affairs"
  },
  ...
  ]
  """
  ipy.embed
  return json.load(open(DATA_DIR+'naics_list.json','r'))

def get_naics_dict():
  """ Returns dict of json naics code to objects

  Response Format:
  [
  {
    "code": 928120,
    "description": "This industry comprises establishments of U.S. and foreign governments primarily engaged in international affairs and programs relating to other nations and peoples.",
    "title": "International Affairs"
  },
  ...
  ]
  """
  naics_dict = {}
  for naics in get_naicslist():
    naics_dict[naics['code']] = naics
  return naics_dict

def get_test_classifiedset():
  """ Returns dictionary of classified NAICS for testing

  Response Format:
  {
  'c7103540-d25d-4f7f-9b4d-984eecf6ff7b': '54',
  'df039e7a-a0b5-4700-9823-1119c771f59f': '51',
  ...
  'fe389cac-3795-4b4c-9d09-39b77e166f5a': '444'
  }
  """
  with open(DATA_DIR+'classified_set.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    d = {}
    for row in spamreader:
      d[row[0]] = row[1]
  return d

def get_hand_classifiedset():
  """ Returns dictionary of classified NAICS that will be submitted

  Response Format:
  {
  'c7103540-d25d-4f7f-9b4d-984eecf6ff7b': '54',
  'df039e7a-a0b5-4700-9823-1119c771f59f': '51',
  ...
  'fe389cac-3795-4b4c-9d09-39b77e166f5a': '444'
  }
  """
  with open(DATA_DIR+'hand_classified_set.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    d = {}
    for row in spamreader:
      d[row[0]] = row[1]
  return d


def get_algo_classifiedset():
  """ Returns dictionary of classified NAICS that will be submitted

  Response Format:
  {
  'c7103540-d25d-4f7f-9b4d-984eecf6ff7b': '54',
  'df039e7a-a0b5-4700-9823-1119c771f59f': '51',
  ...
  'fe389cac-3795-4b4c-9d09-39b77e166f5a': '444'
  }
  """
  with open(DATA_DIR+'algo_classified_set.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    d = {}
    for row in spamreader:
      d[row[0]] = row[1]
  return d

def get_challengeset():
  """ Returns the list of businesses

  Response Format:
  [
  {u'address': u'2136 PLEASANT HILL RD, MARION OH 43302',
  u'description': u'If you are looking for the best prices on any of the Amsoil Products, Feel free to contact Terri or Dwight Lohr Amsoil Dealer Number 5266770',
  u'name': u'marion amsoil dealer',
  u'unique_id': u'ed6ad152-a7d3-4fdc-b3d9-aff1094d3ea5',
  u'website': [u'http://www.amsoil.com']},
  ...
  ]
  """
  return json.load(open(DATA_DIR+'challenge_set.json','r'))

def get_business_types():
  """ Returns dict: unique_id --> type
  If None: could not get a type

  Response Format:
  {
  u'1fe9adec-46f3-48f8-9fdd-4b715115a091': restaurant,
  u'1fee61a2-571d-4789-ac98-3d670bc9acb3': cafe,
  u'1fee61a2-571d-4789-ac98-3d670bc9acb3': None,
  ...
  u'2002c9ca-45a5-49a1-921b-191b2760c89f': museum,
  }
  """
  try:
    return pickle.load(open(DATA_DIR+'business_types.pickle','r'))
  except IOError:
    return {}

def get_naics_data_for_level(code_length):
  naics_data = get_naicslist()
  results = []
  for naics_item in naics_data:
    if len(str(naics_item['code'])) == code_length:
      results.append(naics_item)
  return results

def get_unclassified_business_ids():
  businesses = get_challengeset()
  unclassified_ids = []
  ids = get_classified_business_ids()
  for b in businesses:
    if b['unique_id'] not in ids:
      unclassified_ids.append(b['unique_id'])
  return unclassified_ids

def get_word2vecmodel():
  return word2vec.Word2Vec.load("../data/word2vec_model")

def get_word2vecmodel_brown():
  return word2vec.Word2Vec.load("../data/brown_model")

def get_word2vecmodel_reuters():
  return word2vec.Word2Vec.load("../data/reuters_model")

def get_classified_business_ids():
  test_classified_set = get_test_classifiedset()
  hand_classified_set = get_hand_classifiedset()
  return list(set(test_classified_set.keys()) | set(hand_classified_set.keys()))

def write_row_classified_set(business_uid, naics_code):
  with open(DATA_DIR+'classified_set.csv', 'a') as classified_set:
    wr = csv.writer(classified_set)
    wr.writerow( ( business_uid, naics_code) )

def write_row_hand_classified_set(business_uid, naics_code):
  with open(DATA_DIR+'hand_classified_set.csv', 'a') as hand_classified_set_file:
    wr = csv.writer(hand_classified_set_file)
    wr.writerow( ( business_uid, naics_code) )

if __name__ == '__main__':
  ipy.embed()
