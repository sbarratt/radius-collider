import json
try:
	import IPython as ipy
except:
	pass

with open('../challenge_set.json') as data_file:
	res = json.load(data_file)