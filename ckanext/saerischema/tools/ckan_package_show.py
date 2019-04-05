#!/usr/bin/env python
# 1.01 arb Fri  5 Apr 18:14:19 BST 2019 - if no argument given then list all datasets

# Usage: [datasetname]
#  lists all datasets, or only the given one
#
# To parse the output as JSON use the jq program, for example:
# ./ckan_package_show.py test-dataset-6-title| jq 'del(.organization,.resources)'
# will clean up the JSON output and delete the organization and resources fields.

import urllib2
import urllib
import json
import pprint
import sys
from ckanapi import RemoteCKAN

user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'
dataset = 'dietary-dna-metabarcoding-in-black-browed-albatrosses-derived-from-scats-collected-at-new-island-ste'
dataset = ''

# Read the configuration
ckan_ip = open("/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/ckan_ip.txt").read().replace('\n','')
api_key = open("/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/ckan_api_key.txt").read().replace('\n','')

if len(sys.argv) > 1:
    dataset = sys.argv[1]

# Open the connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)

# Show the dataset,
# can pass either name or id as the id parameter
if dataset:
	result = ckan.call_action('package_show', {'id': dataset} )
else:
	result = ckan.call_action('package_search', {'q': ''} )

RemoteCKAN.close(ckan)

print(json.dumps(result))

exit(0)
