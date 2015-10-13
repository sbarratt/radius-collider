import json
import IPython as ipy

"""

Natural 

"""

"""

'name’: the name of the business
'address’: the address of the business
‘description’: a text description of the business
‘website’: a list of URLs related to the business
‘unique_id’: a unique identifier for this record

"""

with open('challenge_set.json') as data_file:
	res = json.load(data_file)
		ipy.embed()

print res
