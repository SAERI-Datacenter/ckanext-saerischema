#!/usr/bin/env python
import urllib2
import urllib
import json
import pprint

# Upload a resource to a dataset
# We are going to use the Requests Python library for this
# because it's easy to POST a multipart

# Put the details of the resource we're going to create into a dict.

resource_dict = {
	'package_id': 'fd697f3a-1444-4bc8-a8b3-9f59da268727',
	'url':        'dummy-value',
	'upload':     'what is this supposed to be FieldStorage'
}

# Use the json module to dump the dictionary to a string for posting.
resource_string = urllib.quote(json.dumps(resource_dict))
print(resource_string)

import requests
response = requests.post('http://publicamundi/api/action/resource_create',
              data={"package_id":"test_dataset"},
              headers={"X-CKAN-API-Key": "8537dc72-2a84-428a-9038-208e50b597b5"},
              files=[('upload', file('/users/local/arb/MSc/LANDSAT/log.txt'))])

print('Response status code: %d' % response.status_code)
assert response.status_code == 200

print('Response:')
print(response.text)

response_dict = json.loads(response.text)
# or response.json()

print('Response success:')
print(response_dict['success'])

print('Response dict:')
print(response_dict)

print('Result:')
created_resource = response_dict['result']
pprint.pprint(created_resource)

---

# Two ways to call an action:
datasets = ckan.action.package_search(include_private=True, include_drafts=True, q='"test-dataset-3"')
#datasets = ckan.call_action('package_search', {'include_private':True, 'include_drafts':True} )
#print(datasets['count'])
#pprint(datasets)

for result in datasets['results']:
	print("%s = %s" % ( result['id'], result['name']))
	for resource in result['resources']:
		print("  resource %s" % resource['url'])


# See http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.create.resource_create

# test_dataset might have id=fd697f3a-1444-4bc8-a8b3-9f59da268727
# seen from CSW API on Developers tab http://publicamundi/dataset/developers/test_dataset

res = pm.action.resource_create(package_id='fd697f3a-1444-4bc8-a8b3-9f59da268727',
	url='dummy-value',
	name='LC08_L1GT_205021_20171113_20171121_01_T2_TIR.tif',
	format='GEOTIFF',
	upload=open('/users/local/arb/MSc/LANDSAT/log.txt', 'rb'))


