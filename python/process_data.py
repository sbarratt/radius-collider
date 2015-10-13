import json
try:
	import IPython as ipy
except:
	print "Couldn't import IPython"

with open('../challenge_set.json') as data_file:
	res = json.load(data_file)