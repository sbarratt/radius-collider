import json # For loading the data

# For debugging purposes
try:
	import IPython as ipy
except ImportError:
	print "Couldn't import IPython"

import nltk # Natural Language Processing Library, run nltk.download() to get english dictionary and such
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np # Numerical Python Library
from urllib import urlopen
from bs4 import BeautifulSoup

"""

nltk.corpus words, stopwords
from nltk.stem import WordNetLemmatizer
WordPunctTokenizer
BiggramCollocationFinder
BiggramAssocMeasures
lemma_names
"""

stopset = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')
wordnet_lemmatizer = WordNetLemmatizer()

def clean_paragraph(par):
	par.decode('utf-8')
	tokens = tokenizer.tokenize(par)
	tokens = [w for w in tokens if not w in stopset]
	x = []
	for word in tokens:
		if wordnet.synsets(word):
			if len(word) > 1:
				x.append(wordnet_lemmatizer.lemmatize(word.lower()))
	#lemma-ize

	return x

clean_paragraph('Equal Justice For All. At the Law Offices of Wolfley & Wolfley, P.S., in Port Angeles, WA, you will get aggressive legal representation in your personal injury or workers\u2019 compensation case to help you get the compensation you deserve...')

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
		ipy.embed()
		tokens = nltk.wordpunct_tokenize(raw)
		text = nltk.Text(tokens)
		x = []
		for word in text.tokens:
			if wordnet.synsets(word):
			  x.append(word)
		print x
		ipy.embed()
