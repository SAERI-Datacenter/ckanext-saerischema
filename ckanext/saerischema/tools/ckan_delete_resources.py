#!/usr/bin/env python2
#
# This script will delete all resources from datasets which were created
# after a specific date, so you can undo a recent add.
# Change the date in the test below.

import urllib2
import urllib
import json
import pprint    # for pprint.pprint
import csv       # for csv.DictReader
import re        # for re.sub()
from ckanapi import RemoteCKAN
# import our tools from the parent directory
import sys,os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import saerickan

# Configuration
#ckan_ip = "172.16.92.142" # eg. 172.16.92.142:5000 if using paster serve $ini
#api_key = "0317c21c-7d04-48df-8f1b-9989edbd6165"
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'


# -----------------------------------------------------------------------
# Display the content of a dataset, used only for debugging.

def ckan_get_dataset(ds):
	packages_results = ckan.action.package_show(include_private=True, include_drafts=True, id=ds)
	print(packages_results)
	exit(0)

# -----------------------------------------------------------------------
# Check if a dataset exists with the given 'name', returns True if it does.
# The search includes private and draft datasets.
# The given name must match exactly.

def ckan_search_dataset(ds):
	if ds:
		packages_results = ckan.action.package_search(include_private=True, include_drafts=True, q='"%s"' % ds)
	else:
		packages_results = ckan.action.package_search(include_private=True, include_drafts=True, q='')
	if packages_results['count'] < 1: return ''
	# Check for an EXACT match not a substring
	for package_result in packages_results['results']:
		print('Found %s' % package_result['name'])
		if package_result['name'] == ds:
			print('Exact')
	return package_result['id']

# -----------------------------------------------------------------------
# The test for whether to remove a dataset, return True to remove, False to keep

def test_dataset_for_removal(ds):
	if ds['metadata_created'] > '2019-03-27':
		return True
	else:
		return False

def test_resource_for_removal(rs):
	if rs['created'] > '2019-03-29':
		return True
	else:
		return False


# -----------------------------------------------------------------------
# Delete all datasets which match the test above

def ckan_delete_datasets():
	# Search for ALL datasets
	packages_results = ckan.action.package_search(include_private=True, include_drafts=True, q='', rows=999)
	print('Got %s results' % packages_results['count'])
	if packages_results['count'] < 1: return ''
	for package_result in packages_results['results']:
		print('Found %s from %s with %d resources in %s' % (package_result['id'], package_result['metadata_created'], len(package_result['resources']), package_result['name']))
		if (len(package_result['resources']) > 0) and test_dataset_for_removal(package_result):
			for resource in package_result['resources']:
				if test_resource_for_removal(resource):
					print('  delete %s %s %s' % (resource['id'], resource['created'], resource['name']))
					result = ckan.call_action('resource_delete', { 'id': resource['id'] })
					if result != None:
						print('ERROR delete %s from %s returned an error' % (resource['name'], package_result['name']))
						pprint.pprint(result)
				else:
					print('  keep   %s %s %s' % (resource['id'], resource['created'], resource['name']))
		else:
			true
			#print('keeping dataset %s' % package_result['name'])


# -----------------------------------------------------------------------
# MAIN

# Read the configuration
ckan_ip = open("/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/ckan_ip.txt").read().replace('\n','')
api_key = open("/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/ckan_api_key.txt").read().replace('\n','')

# Open a connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)

# Delete the datasets
ckan_delete_datasets()

# Close the connection to CKAN
RemoteCKAN.close(ckan)

exit(0)
