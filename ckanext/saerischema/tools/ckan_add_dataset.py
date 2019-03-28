#!/usr/bin/env python2
# Create a dataset from a CSV file
# 1.11 arb Mon 25 Mar 18:31:53 GMT 2019 - fix access limitations mapping
# 1.10 arb Tue  5 Feb 12:34:18 GMT 2019 - many improvements and fixes
# 1.05 arb Wed 30 Jan 10:18:31 GMT 2019 - remove apostrophes from keywords
# 1.04 arb Tue 29 Jan 11:44:09 GMT 2019 - csv_filename can be first parameter
# 1.03 arb Mon Jan 28 18:17:26 GMT 2019 - add dataset to group
# 1.02 arb Wed 23 Jan 15:38:34 GMT 2019 - added config to ignore Incomplete entries (status=0)
# 1.01 arb Wed 23 Jan 15:17:20 GMT 2019 - read config from files
# 1.00 arb Tue 15 Jan 18:35:07 GMT 2019
#
# Reads CKAN server IP address from ckan_ip.txt
# Reads CKAN sysadmin API key from  ckan_api_key.txt
#
# 0. Read CSV file mapping topic_category to group(theme) name
# 1. Read CSV file containing list of datasets
# 2. Check that dataset does not already exist (how?)
# 3. Map from the CSV columns to the CKAN fields
# 4. Check that the organisation already exists
# 5. Check that values being entered match expected values (eg. region, language, status, etc)
# 6. Convert the 'spatial' field like the plugin would do
# 7. Call package_create

from __future__ import print_function
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
# ckan_ip.txt = "172.16.92.142" # eg. 172.16.92.142:5000 if using paster serve $ini
# ckan_api_key.txt = "0317c21c-7d04-48df-8f1b-9989edbd6165"
ignore_incomplete_datasets = True
only_add_first_entry = False
csv_filename = "montserrat_metadata20190322.csv"
access_limitations_file = "../metadata_form_options_access_limitations.txt"
user_agent = 'ckanapiexample/1.0 (+http://example.com/my/website)'
default_contact_consent = '0'
default_permit_id = ''
dry_run = False

# The metadata records are read from a CSV file which is assumed to have these columns:
# ['region', 'organisation', 'id_text', 'unique_resource_id', 'title', 'language', 'abstract', 'topic_category', 'keywords', 'temporal_extent_start', 'temporal_extent_end', 'dataset_reference_date', 'lineage', 'w_long', 's_lat', 'e_long', 'n_lat', 'spatial_reference_system', 'responsible_organisation_name', 'contact_mail_address', 'responsible_party_role', 'frequency_update', 'limitations_access', 'use_constraints', 'data_format', 'accuracy', 'metadata_date', 'metadata_point_contact', 'resource_type', 'original_title', 'id', 'status', 'x_location', 'y_location']

# The CSV column names are mapped to CKAN schema field names:
map_CSV_to_CKAN = {
	'title':    'title',
	'abstract': 'notes',
	'keywords': 'tag_string',
	'region':   'saeri_region',
	'language': 'saeri_language',
	'topic_category':  'saeri_topic_category',
	'temporal_extent_start':  'saeri_temporal_extent_start',
	'temporal_extent_end':    'saeri_temporal_extent_end',
	'dataset_reference_date': 'saeri_dataset_reference_date',
	'lineage': 'saeri_lineage',
	'w_long':  'saeri_west_longitude',
	's_lat':   'saeri_south_latitude',
	'e_long':  'saeri_east_longitude',
	'n_lat':   'saeri_north_latitude',
	'spatial_reference_system': 'saeri_spatial_reference_system',
	'responsible_organisation_name': 'saeri_responsible_organisation_name',
	'contact_mail_address':   'saeri_contact_mail_address',
	'responsible_party_role': 'saeri_responsible_party_role',
	'limitations_access':  'saeri_access_limitations',
	'use_constraints':     'saeri_use_constraints',
	'data_format':      'saeri_data_format',
	'frequency_update': 'saeri_update_frequency',
	'accuracy':         'saeri_accuracy',
	'resource_type':    'saeri_resource_type',
	'original_title':   'saeri_original_title',
	'metadata_date':    'saeri_metadata_date',
	'metadata_point_contact': 'saeri_metadata_point_of_contact',
	'unique_resource_id':     'saeri_unique_resource_id',
	'status':       'saeri_status',
	'organisation': 'owner_org',
	# The following are NOT in the CSV file, but might be in the future.
	# (these names are used lower down to give a default value, so take care)
	'contact_consent':  'saeri_contact_consent',
	'permit_id':        'saeri_research_permit_application_id',
}

# Map from the CSV use_constraints to CKAN license_id
map_saeri_use_constraints_to_license_id = {
	'notcommercial' : 'other-nc',     # Not for commercial use
	'notfornav'     : 'notspecified', # Not to be used for navigational purposes
	'researchonly'  : 'other-nc',     # To be used for research only
	'open'          : 'other-open',   # Open
	'openbut'       : 'other-at',     # Open, but copyright and/or Intellectual Property Rights apply
	'restricted'    : 'other-closed', # Restricted
	'restrictedbut' : 'other-closed', # Restricted, but open subject to limitations and prior agreement with responsible organisation. Copyright must be cited
}


# -----------------------------------------------------------------------
# Read the "metadata_form_options_*.txt" files which map the content of
# the CSV file and what is shown in a drop-down menu into the content of
# the database and what is used as the 'value' in the html <option> tag.
# The files are tab separated, first column is the internal value and the
# second is what is displayed and in the CSV.
# eg.
# metadata_form_options_access_limitations.txt has a line:
# mil	Restricted because of defence and military issue
# So the menu shows "Restricted..." but the database stored "mil"
# When reading the CSV we need to convert from the second to the first.
# NOTE this function is not required and can be removed!
def read_metadata_form_options_into_dict(options_filename):
	options_fp = open("../" + options_filename)
	options_csv_reader = csv.reader(options_fp, delimiter='\t', quoting=csv.QUOTE_NONE)
	for options_row in options_csv_reader:
		print(options_row)
	exit(0)

# -----------------------------------------------------------------------
# This function has been moved into saerickan.py
# Read the group definition CSV file to map from
# our topic_category column to a group (theme) name.
# The topic_category column is in the csvname column in this CSV.
# CSV is:
# csvname,group,title,description,logo
# Returns a dictionary.
# def create_mapping_topic_category_to_group():


# -----------------------------------------------------------------------
# Map from the values inside the CSV file into the values stored in the database
# The latter values are also used as the 'value' attribute of the html <options>
# tag in the drop-down menu when editing the dataset.

map_csv_to_access_limitation = {}

def convert_saeri_access_limitations(saeri_access_limitations):
	global map_csv_to_access_limitation

	saeri_access_limitations = saeri_access_limitations.lower().strip()

	# Read TSV file first time round
	if len(map_csv_to_access_limitation) == 0:
		fp = open(access_limitations_file, 'r')
		for line in fp:
			(key, desc) = line.lower().strip().split('\t')
			map_csv_to_access_limitation[desc] = key
		fp.close()

	if saeri_access_limitations in map_csv_to_access_limitation:
		return map_csv_to_access_limitation[saeri_access_limitations]
	else:
		print("WARNING: access limitation unknown: %s" % saeri_access_limitations)

	# If the input values don't have a one-to-one match we have to guess:
	if 'open access' in saeri_access_limitations:
		return 'open'
	if 'military' in saeri_access_limitations:
		return 'mil'
	if 'commerc' in saeri_access_limitations:
		return 'com-dept'
	if 'environ' in saeri_access_limitations:
		return 'env-dept'
	# The default value is:
	return 'env-com-dept'


# -----------------------------------------------------------------------
# Map use constraints from CSV, mostly free-form text so no accurate mapping.

def convert_saeri_use_constraints(saeri_use_constraints):
	saeri_use_constraints = saeri_use_constraints.lower()

	# Possible return values are:
	# notcommercial, notfornav, researchonly, open, openbut, restricted, restrictedbut
	# Input values are plain text so don't have a one-to-one match
	# so most of the time we have to guess:
	if 'open acces' in saeri_use_constraints:
		return 'open'
	if 'restricted' in saeri_use_constraints:
		return 'restrictedbut'
	# The default value is:
	return 'openbut'

# -----------------------------------------------------------------------
# Check if an organisation exists in CKAN, returns True if it does.
# Uses an exact match so be careful about capital/lowercase.
# Typically we store organisation 'name' lowercase.

def ckan_check_organisation_exists(org):
	organisations_data = ckan.action.organization_list(all_fields=True)
	organisations_list = [x['name'] for x in organisations_data]
	return org in organisations_list

# -----------------------------------------------------------------------
# Display the content of a dataset.
# Only for debugging.

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

def ckan_add_dataset_from_csv_dict(row, dataset_name_to_be_updated):
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
	dataset_dict['name'] = saerickan.saerickan_name_from_title(dataset_dict['title'])

	# For testing: only process the named dataset
	if dataset_name_to_be_updated and (dataset_dict['name'] != dataset_name_to_be_updated):
		return

	# Lower-case organisation name
	dataset_dict['owner_org'] = dataset_dict['owner_org'].lower()

	# Remove apostrophes from the keywords (tag_string)
	dataset_dict['tag_string'] = re.sub("'", "", dataset_dict['tag_string'])

	# Group (theme) membership
	# Take the topic_category, map to the name of an existing group
	# put it into a dictionary and put that into a list (assuming only one group)
	if row['topic_category']:
		dataset_dict['groups'] = [ { 'name': topic_category_to_group_dict[row['topic_category']] } ]

	# The CSV is missing two columns: contact_consent and permit_id
	# If they are not present then add a default value.
	if not 'saeri_contact_consent' in dataset_dict:
		dataset_dict['saeri_contact_consent'] = default_contact_consent

	if not 'saeri_research_permit_application_id' in dataset_dict:
		dataset_dict['saeri_research_permit_application_id'] = default_permit_id

	# Some of the columns require conversion from the plain text to the value
	# which is stored in the database. These same database values are also used
	# as the 'value' in the html <options> tag for drop-down menus so they are
	# defined in the metadata_for_options_*.txt files.
	dataset_dict['saeri_access_limitations'] = convert_saeri_access_limitations(dataset_dict['saeri_access_limitations'])
	dataset_dict['saeri_use_constraints'] = convert_saeri_use_constraints(dataset_dict['saeri_use_constraints'])

	# License and whether the dataset is "open" or not,
	# These are additional fields in CKAN calculated from our own fields.
	# isopen is only true if the dataset is truly fully open access
	if dataset_dict['saeri_use_constraints'] == 'open':
		dataset_dict['isopen'] = True
	else:
		dataset_dict['isopen'] = False
	# license_id can be: notspecified, other-open, other-closed, other-at, other-nc
	if dataset_dict['saeri_use_constraints'] in map_saeri_use_constraints_to_license_id:
		dataset_dict['license_id'] = map_saeri_use_constraints_to_license_id[dataset_dict['saeri_use_constraints']]
	else:
		dataset_dict['license_id'] = 'notspecified'
	#dataset_dict['license_title'] = '' # XXX maybe this will get added automatically?

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
	if not dry_run:
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

# CSV filename is first parameter
if len(sys.argv) > 1:
	csv_filename = sys.argv[1]
dataset_name_to_be_updated = ''
if len(sys.argv) > 2:
	dataset_name_to_be_updated = sys.argv[2]

# Read the configuration
ckan_ip = open("/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/ckan_ip.txt").read().replace('\n','')
api_key = open("/usr/lib/ckan/default/src/ckanext-saerischema/ckanext/saerischema/tools/ckan_api_key.txt").read().replace('\n','')

# Read CSV from theme plugin
topic_category_to_group_dict = saerickan.saerickan_create_mapping_topic_category_to_group()

# Read in the CSV file
fp = open(csv_filename)
reader = csv.DictReader(fp)

# Open the connection to the CKAN server
ckan = RemoteCKAN('http://%s' % ckan_ip, apikey=api_key, user_agent=user_agent)

# Process each row
for row in reader:
	ckan_add_dataset_from_csv_dict(row, dataset_name_to_be_updated)
	# Stop after the first row?
	if only_add_first_entry:
		break

# Close
RemoteCKAN.close(ckan)
fp.close()

exit(0)
