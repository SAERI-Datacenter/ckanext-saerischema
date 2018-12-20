#!/usr/bin/env python2

# Test the CKAN API
# Debug the request like this: print(request.headers)
# or run "netcat -l 8080" and change URL to localhost:8080

import urllib2
import urllib
import json
import pprint

ip = "172.16.92.142"
api_key = '0317c21c-7d04-48df-8f1b-9989edbd6165'

# Construct the URL with the IP address
# Can also include parameters like "?include_private=True&include_drafts=True"
url='http://%s/api/3/action/package_search' % (ip)

request = urllib2.Request(url)

# Add headers to become sysadmin user
request.add_header('X-CKAN-API-Key', api_key)
request.add_header('Authorization', api_key)


# Send the request

# Options can be None or an encoded dictionary
post_parameters={ 'include_private': True, 'include_drafts': True }
post_arg = None
post_arg = urllib.urlencode(post_parameters)

try:
	response_dict = json.loads(urllib2.urlopen(request, post_arg).read())
except:
	print("ERROR IN API")
	exit(0)

#print(response_dict)
if response_dict['success'] == True: print('OK')
if response_dict['success'] != True: print('ERROR')

if 'count' in response_dict['result']: print("Got %d results" % response_dict['result']['count'])
#print('result is : %s' % response_dict['result'])
pprint.pprint(response_dict['result'])


