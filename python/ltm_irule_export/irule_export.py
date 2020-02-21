import requests
import json
import sys
import time
import argparse
import getpass

requests.packages.urllib3.disable_warnings()

# Get command line arguments 
parser = argparse.ArgumentParser(description='F5 Big-IP iApp conversion utility')
parser.add_argument('--host', help='BIG-IP IP or Hostname', required=True)
parser.add_argument('--username', help='BIG-IP Username', required=True)
parser.add_argument('--irule', help='iRule Name to be exported', required=True)
parser.add_argument('--password', help='BIG-IP Password')
args = vars(parser.parse_args())

BIGIP_URL_BASE = 'https://%s/mgmt/tm' % args['host']
FILENAME = 'irule_%s.json' % (args['irule'])

# Setup Password
if args['password'] != None:
    password = args['password']
else:
    print("User: %s, enter your password: " % args['username'])
    password = getpass.getpass()

# REST resource for BIG-IP that all other requests will use
bigip = requests.session()
bigip.verify = False
bigip.headers.update({'Content-Type' : 'application/json'})
bigip.auth = (args['username'], password)

try:
    response = bigip.get('%s/ltm/rule/%s' % (BIGIP_URL_BASE, args['irule']))
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4))
    else:
        print('Could not get iRule')
except:
    print('Communication failure with BigIP: %s' % args['host'])