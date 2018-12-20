#!/usr/bin/env python2

ip = "172.16.92.142"
api_key = "0317c21c-7d04-48df-8f1b-9989edbd6165"
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'

from ckanapi import RemoteCKAN
from pprint import pprint

ckan = RemoteCKAN('http://%s' % ip, apikey=api_key, user_agent=user_agent)

# Two ways to call an action:
datasets = ckan.action.package_search(include_private=True, include_drafts=True, q='"test-dataset-3"')
#datasets = ckan.call_action('package_search', {'include_private':True, 'include_drafts':True} )
#print(datasets['count'])
#pprint(datasets)

for result in datasets['results']:
	print("%s = %s" % ( result['id'], result['name']))
	for resource in result['resources']:
		print("  resource %s" % resource['url'])

RemoteCKAN.close(ckan)

exit(0)

# See http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.create.resource_create

# test_dataset might have id=fd697f3a-1444-4bc8-a8b3-9f59da268727
# seen from CSW API on Developers tab http://publicamundi/dataset/developers/test_dataset

res = pm.action.resource_create(package_id='fd697f3a-1444-4bc8-a8b3-9f59da268727',
	url='dummy-value',
	name='LC08_L1GT_205021_20171113_20171121_01_T2_TIR.tif',
	format='GEOTIFF',
	upload=open('/users/local/arb/MSc/LANDSAT/log.txt', 'rb'))

# Or by calling the generic call_action function with the actual function name as a parameter:
#res = pm.call_action('resource_create',
#	{ 'package_id' : 'test_dataset' },
#	files = { 'upload' : open('/users/local/arb/MSc/LANDSAT/log.txt', 'rb') } )
print res
