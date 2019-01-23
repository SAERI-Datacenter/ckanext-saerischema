#!/usr/bin/env python2
# Create a dataset from a CSV file
# 1.02 arb Wed 23 Jan 15:38:34 GMT 2019 - added config to ignore Incomplete entries (status=0)
# 1.01 arb Wed 23 Jan 15:17:20 GMT 2019 - read config from files
# 1.00 arb Tue 15 Jan 18:35:07 GMT 2019
#
# Reads CKAN server IP address from ckan_ip.txt
# Reads CKAN sysadmin API key from  ckan_api_key.txt
#
# 1. Read CSV file
# 2. Check that dataset does not already exist (how?)
# 3. Map from the CSV columns to the CKAN fields
# 4. Check that the organisation already exists
# 5. Check that values being entered match expected values (eg. region, language, status, etc)
# 6. Convert the 'spatial' field like the plugin would do
# 7. Call package_create

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
ignore_incomplete_datasets = True
only_add_first_entry = False
csv_filename="metadata_FK_export190122.csv"
#ckan_ip = "172.16.92.142" # eg. 172.16.92.142:5000 if using paster serve $ini
#api_key = "0317c21c-7d04-48df-8f1b-9989edbd6165"
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'

# CSV fields are:
# ['region', 'organisation', 'id_text', 'unique_resource_id', 'title', 'language', 'abstract', 'topic_category', 'keywords', 'temporal_extent_start', 'temporal_extent_end', 'dataset_reference_date', 'lineage', 'w_long', 's_lat', 'e_long', 'n_lat', 'spatial_reference_system', 'responsible_organisation_name', 'contact_mail_address', 'responsible_party_role', 'frequency_update', 'limitations_access', 'use_constraints', 'data_format', 'accuracy', 'metadata_date', 'metadata_point_contact', 'resource_type', 'original_title', 'id', 'status', 'x_location', 'y_location']

# CSV column mapping to CKAN field name
map_CSV_to_CKAN = {
	'title': 'title',
	'abstract': 'notes',
	'keywords': 'tag_string',
	'region': 'saeri_region',
	'language': 'saeri_language',
	'topic_category': 'saeri_topic_category',
	'temporal_extent_start': 'saeri_temporal_extent_start',
	'temporal_extent_end': 'saeri_temporal_extent_end',
	'dataset_reference_date': 'saeri_dataset_reference_date',
	'lineage': 'saeri_lineage',
	'w_long': 'saeri_west_longitude',
	's_lat': 'saeri_south_latitude',
	'e_long': 'saeri_east_longitude',
	'n_lat': 'saeri_north_latitude',
	'spatial_reference_system': 'saeri_spatial_reference_system',
	'responsible_organisation_name': 'saeri_responsible_organisation_name',
	'contact_mail_address': 'saeri_contact_mail_address',
	'responsible_party_role': 'saeri_responsible_party_role',
	'limitations_access': 'saeri_access_limitations',
	'use_constraints': 'saeri_use_constraints',
	'data_format': 'saeri_data_format',
	'frequency_update': 'saeri_update_frequency',
	'accuracy': 'saeri_accuracy',
	'resource_type': 'saeri_resource_type',
	'original_title': 'saeri_original_title',
	'metadata_date': 'saeri_metadata_date',
	'metadata_point_contact': 'saeri_metadata_point_of_contact',
	'unique_resource_id': 'saeri_unique_resource_id',
	'status': 'saeri_status',
	'organisation': 'owner_org',
}

# -----------------------------------------------------------------------
# Convert title to name by lowercase, remove spaces, etc
# The name will be used for the URL so it has to be sanitised.
# Ultimately it will be unique for each dataset.

def ckan_name_from_title(title):
	# replace all spaces by a dash
	name = re.sub(" +", "-", title.lower())

	# keep only alpha-num and dashes
	name = re.sub("[^a-z0-9-]", "", name)

	# remove spaces from start and end, and squash multiple spaces
	name = re.sub("^-", "", name)
	name = re.sub("-$", "", name)
	name = re.sub("-+", "-", name)

	# return a maximum length of 100
	return name[:100]

# -----------------------------------------------------------------------
# Check if an organisation exists in CKAN, returns True if it does.
# Uses an exact match so be careful about capital/lowercase.
# Typically we store organisation 'name' lowercase.

def ckan_check_organisation_exists(org):
	organisations_data = ckan.action.organization_list(all_fields=True)
	organisations_list = [x['name'] for x in organisations_data]
	return org in organisations_list

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

def ckan_check_dataset_exists(ds):
	packages_results = ckan.action.package_search(include_private=True, include_drafts=True, q='"%s"' % ds)
	if packages_results['count'] < 1: return False
	ds_exists = False
	# Check for an EXACT match not a substring
	for package_result in packages_results['results']:
		if package_result['name'] == ds:
			ds_exists = True
	return ds_exists

# -----------------------------------------------------------------------
# Add a dataset to CKAN, or update it if it already exists.
# The dataset fields are defined in the dictionary called row
# which has been extracted from one line in a CSV file.

def ckan_add_dataset_from_csv_dict(row):
	#print("%s" % (ckan_name_from_title(row['title'])))
	#print("%s = %s" % (ckan_name_from_title(row['title']), row['unique_resource_id']))
	#return

	# Ignore incomplete entries, if desired
	if row['status'] != '1' and ignore_incomplete_datasets:
		print('Incomplete (ignoring): %s' % row['title'])
		return

	package_create_or_update_action = 'package_create'

	# Convert every field from the CSV into a field for CKAN
	# Unknown fields (i.e. CSV column names) will be reported.
	# Some are useless and will be silently ignored.
	dataset_dict = {}
	for key in row.keys():
		if key in map_CSV_to_CKAN:
			#print("MAP %s->%s (%s)" % (key, map_CSV_to_CKAN[key], row[key]))
			dataset_dict[map_CSV_to_CKAN[key]] = row[key]
		else:
			# Only report columns being ignored if they are unknown
			if key != 'id_text' and key != 'id' and key != 'x_location' and key != 'y_location':
				print("IGNORE: %s (%s)" % (key, row[key]))

	# Create the name (which forms the URL) from the title
	# by removing spaces and non-alpha chars.
	dataset_dict['name'] = ckan_name_from_title(dataset_dict['title'])

	# Lower-case organisation name
	dataset_dict['owner_org'] = dataset_dict['owner_org'].lower()

	# Spatial component is GeoJSON converted from bounding box coords
	spatial_string = saerickan.saerickan_convert_bbox_to_geojson(
		dataset_dict['saeri_spatial_reference_system'],
		dataset_dict['saeri_north_latitude'],
		dataset_dict['saeri_south_latitude'],
		dataset_dict['saeri_west_longitude'],
		dataset_dict['saeri_east_longitude'])
	if spatial_string:
		dataset_dict['spatial'] = spatial_string
		#print(dataset_dict['spatial'])

	# See if organisation already exists (it must)
	if not ckan_check_organisation_exists(dataset_dict['owner_org']):
		print("ERROR: Organisation does not exist: '%s'" % dataset_dict['owner_org'])
		return

	# See if dataset already exists (it must not)
	if ckan_check_dataset_exists(dataset_dict['name']):
		print("NOTE: Dataset already exists, will update: '%s'" % dataset_dict['name'])
		package_create_or_update_action = 'package_update'

	# Create or update the dataset using package_create/package_update
	#print("Creating: %s" % dataset_dict['name'])
	#pprint.pprint(dataset_dict)
	result = ckan.call_action(package_create_or_update_action, dataset_dict)
	if 'name' in result:
		print("OK: %s for %s" % (package_create_or_update_action, dataset_dict['name']))
	else:
		print("ERROR: %s failed for %s" % (package_create_or_update_action, dataset_dict['name']))
	# Should be able to test this? assert response_dict['success'] is True
	#print("Dataset %s returned:" % package_create_or_update_action)
	#pprint.pprint(result)
	# Use the json module to dump the dictionary to a string for posting.
	##data_string = urllib.quote(json.dumps(dataset_dict))

	# Could upload a file at the same time using:
	# Or by calling the generic call_action function with the actual function name as a parameter:
	#res = pm.call_action('resource_create',
	#	{ 'package_id' : 'test_dataset' },
	#	files = { 'upload' : open('/users/local/arb/MSc/LANDSAT/log.txt', 'rb') } )
	#print res

# -----------------------------------------------------------------------
# MAIN

# Read the configuration
ckan_ip = open("ckan_ip.txt").read().replace('\n','')
api_key = open("ckan_api_key.txt").read().replace('\n','')

# Read in the CSV file
fp = open(csv_filename)
reader = csv.DictReader(fp)

# Open the connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)

# Process each row
for row in reader:
	ckan_add_dataset_from_csv_dict(row)
	# Stop after the first row?
	if only_add_first_entry:
		break

# Close
RemoteCKAN.close(ckan)
fp.close()

exit(0)
