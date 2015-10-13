import json
try:
	import IPython as ipy

"""
Natural 
"""

with open('../challenge_set.json') as data_file:
	res = json.load(data_file)
		ipy.embed()
print res
