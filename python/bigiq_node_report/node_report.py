import requests
import json
import sys
import time
import argparse
import getpass

requests.packages.urllib3.disable_warnings()

# Get command line arguments 
parser = argparse.ArgumentParser(description='F5 Big-IQ Virtual Server Report Utility')
parser.add_argument('--host', help='BIG-IQ IP or Hostname', required=True)
parser.add_argument('--username', help='BIQ-IQ Username', required=True)
parser.add_argument('--node', help='IP address of server node. Ex. \'10.1.10.200\'', required=True)
parser.add_argument('--auth-provider', help='BIG-IQ External Auth Provider name (Optional. Default is local auth: \"tmos\")', default='tmos')
parser.add_argument('--password', help='BIG-IQ Password (Optional. Otherwise getpass prompted)')
args = vars(parser.parse_args())

BIGIQ_URL_BASE = 'https://%s/mgmt' % args['host']

# Setup Password
if args['password'] != None:
    password = args['password']
else:
    print('User: %s, enter your password: ' % args['username'])
    password = getpass.getpass()

# REST resource for BIG-IQ that all other requests will use
bigiq = requests.session()
bigiq.verify = False
bigiq.headers.update({'Content-Type' : 'application/json'})

# Get Auth Token
user_data = {
    'username': args['username'],
    'password': password,
    'loginProviderName': args['auth_provider']
}
try:
    response = bigiq.post('%s/shared/authn/login' % BIGIQ_URL_BASE, data=json.dumps(user_data))
    if response.status_code != 200:
        print('Invalid login')
        sys.exit()
except:
    print('Connection Unsuccessful')
    sys.exit(1)
else:
    token = response.json()['token']['token']
    bigiq.headers.update({'X-F5-Auth-Token' : token})

# Initialize report dict to be used for JSON export
report = {
    'target': { 'ip': args['node'] },
    'devices': []
}

# Get Node Inventory from BIG-IQ
node_list = bigiq.get('%s/cm/adc-core/working-config/ltm/node' % BIGIQ_URL_BASE).json()['items']

# Get Pool Inventory from BIG-IQ
pool_list = bigiq.get('%s/cm/adc-core/working-config/ltm/pool' % BIGIQ_URL_BASE).json()['items']

# Get Virtual Server Inventory from BIG-IQ
vs_list = bigiq.get('%s/cm/adc-core/working-config/ltm/virtual' % BIGIQ_URL_BASE).json()['items']


# Check for node match
for node in node_list:
    if args['node'] == node['address']:
        node_hit = {
            'name': node['deviceReference']['name'],
            'pools': [],
            'virtuals': []
        }
        
        # Loop through all device pools and check for node membership
        for pool in pool_list:
            if pool['deviceReference']['id'] == node['deviceReference']['id']:
                member_list = bigiq.get(pool['membersCollectionReference']['link'].replace('localhost', args['host'])).json()['items']
                for member in member_list:
                    if args['node'] == member['nodeReference']['address']:
                        node_hit['pools'].append({
                            'name': pool['name'],
                            'member_name': member['name']
                        })

                        # Loop through all virtuals with this pool as a default
                        for vs in vs_list:
                            if vs['deviceReference']['id'] == node['deviceReference']['id'] and \
                            'poolReference' in vs.keys() and \
                            vs['poolReference']['id'] == pool['id']:
                                node_hit['virtuals'].append(vs['name'])
       
        report['devices'].append(node_hit)

# Print results in json format
print(json.dumps(report, indent=4))