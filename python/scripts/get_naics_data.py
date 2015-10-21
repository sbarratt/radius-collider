"""
python/get_naics_data.py

Script to dump descriptions from CodeForAmerica NAICS API into ../naics_list.json
"""

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import loader
import requests
import csv
import json


def url(code):
    return "http://api.naics.us/v0/q?year=2012&code={}".format(code)

results = []
descriptions = loader.get_naicslist()
reader = csv.reader(descriptions)

i = 0
for row in reader:
    i += 1
    print i  # just to know status of process
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
