import csv
import json
import requests

def url(code):
  return "http://api.naics.us/v0/q?year=2012&code={}".format(code)

results = []

with open('../NAICS_descriptions.csv', 'r') as descriptions:

    reader = csv.reader(descriptions)
    i = 0
    for row in reader:
      i += 1
      print i
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


with open('../data.json', 'w') as jsonfile:
  json.dump(results, jsonfile)
