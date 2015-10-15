import json # For loading the data

# For debugging purposes
try:
	import IPython as ipy
except ImportError:
	print "Couldn't import IPython"

import nltk # Natural Language Processing Library, run nltk.download() to get english dictionary and such
from nltk.corpus import wordnet
import numpy as np # Numerical Python Library
from urllib import urlopen
from bs4 import BeautifulSoup

"""
Keys: We must implement the whole thing in scala once we're done 
(to maximize points, possibly put it in spark)

NAICS (North America Industry Classification System)
2 through 6-digit hierarchical classification system 
*first 2 = economic sector
*third = subsector
*fourth = industry group
*fifth = NAICS industry
*sixth = national industry

19256 NAICS codes
"""

with open('../challenge_set.json') as data_file:
	businesses = json.load(data_file)

for business in businesses:
	for url in business['website']:
		html = urlopen(url).read().decode('utf8')
		raw = BeautifulSoup(html).get_text()
		tokens = nltk.wordpunct_tokenize(raw)
		text = nltk.Text(tokens)
		x = []
		for word in text.tokens:
			if wordnet.synsets(word):
			  x.append(word)
		print x
		ipy.embed()
