#!/usr/bin/env python
import urllib2
import urllib
import json
import pprint
import sys
from ckanapi import RemoteCKAN

user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'
dataset = 'dietary-dna-metabarcoding-in-black-browed-albatrosses-derived-from-scats-collected-at-new-island-ste'

# Read the configuration
ckan_ip = open("ckan_ip.txt").read().replace('\n','')
api_key = open("ckan_api_key.txt").read().replace('\n','')

if len(sys.argv) > 1:
    dataset = sys.argv[1]

# Open the connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)

# Show the dataset,
# can pass either name or id as the id parameter
result = ckan.call_action('package_show', {'id': dataset} )

pprint.pprint(result)

RemoteCKAN.close(ckan)
