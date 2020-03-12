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
parser.add_argument('--file', help='Name of CVS file', required=True)
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

routes = []
# Read in CVS file
try:
    f = open(args['file'], 'r')
    for line in f:
        # Remove newline characters and whitespace characters
        line = str(line).replace('\n','').replace('\r','').replace(' ', '')
        fields = line.split(',')
        routes.append({'name': fields[0], 'network': fields[1], 'gw': fields[2]})
except Exception as e:
    print('Encountered problem reading file: %s' % args['file'])
    sys.exit(1)

# Push Routes to BigIP
try:
    for route in routes:
        response = bigip.post('%s/net/route/' % (BIGIP_URL_BASE), data=json.dumps(route))
        if response.status_code == 200:
            print('Success creating route %s' % str(route))
        else:
            print('Failed creating route %s with message %s' % (str(route), response.text))
except Exception as e:
    print('Communication failure with BigIP: %s' % args['host'])