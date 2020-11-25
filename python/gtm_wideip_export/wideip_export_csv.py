import requests
import json
import sys
import time
import argparse
import getpass

requests.packages.urllib3.disable_warnings()

FILENAME = 'wips.csv'

# Get command line arguments 
parser = argparse.ArgumentParser(description='F5 GTM WideIP export (A record type only)')
parser.add_argument('--host', help='BIG-IP IP or Hostname', required=True)
parser.add_argument('--username', help='BIG-IP Username', required=True)
parser.add_argument('--password', help='BIG-IP Password')
args = vars(parser.parse_args())

BIGIP_URL_BASE = 'https://%s/mgmt/tm' % args['host']

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
    response = bigip.get('%s/gtm/wideip/a' % (BIGIP_URL_BASE))
    if response.status_code == 200:
        wip_list = response.json()['items']

        # Open CSV file for writing
        f = open(FILENAME, 'w')
        # Iterate through wip list to export to CVS
        for wip in wip_list:
            f.write('%s,%s\n' % (wip['name'], wip['description']))
        # Close file
        f.close() 
    else:
        print('Could not get WideIPs')
except:
    print('Communication failure with BigIP: %s' % args['host'])