import json # For loading the data

# For debugging purposes
try:
	import IPython as ipy
except:
	print "Couldn't import IPython"

import nltk # Natural Language Processing Library
import numpy as np # Numberical Python Library

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
	res = json.load(data_file)

ipy.embed()