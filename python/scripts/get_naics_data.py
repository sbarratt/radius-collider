"""
python/get_naics_data.py

Script to dump descriptions from CodeForAmerica NAICS API into ../naics_list.json
"""

import csv
import json
import requests

def url(code):
  return "http://api.naics.us/v0/q?year=2012&code={}".format(code)

results = []

with open('../../naics_list.json', 'r') as descriptions:

    reader = csv.reader(descriptions)
    i = 0
    for row in reader:
      i += 1
      print i # just to know status of process
      code = row[0]
      r = requests.get(url(code))
      obj = json.loads(r.content)

      decriptionList = obj.get("description")
      description = " ".join(decriptionList) if decriptionList else None

      if description and not description.startswith("See industry description for"):
        newObj = {
          "code": obj.get("code"),
          "description": description,
          "title": obj.get("title")
        }
        results.append(newObj)

with open('../../naics_list.json', 'w') as jsonfile:
  json.dump(results, jsonfile)