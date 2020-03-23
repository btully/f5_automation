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
parser.add_argument('--username', help='BIG-IP Username', required=True)
parser.add_argument('--vip', help='IP address and Port of the BigIP virtual server. Ex. \'10.1.10.200:443\'', required=True)
parser.add_argument('--password', help='BIG-IP Password (Optional. Otherwise getpass prompted)')
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
user_data = {'username': args['username'], 'password': password}
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


# Separate IP and port from VIP argument
(ip, port) = args['vip'].split(':')

# Initialize report dict to be used for JSON export
report = {
    'target': { 'ip': ip, 'port': port },
    'devices': [],
    'defaultPool': None,
    'iRules': []
}

# Get Virtual Server Inventory from BIG-IQ
vs_list = bigiq.get('%s/cm/adc-core/working-config/ltm/virtual' % BIGIQ_URL_BASE).json()['items']

device_ref = []
vs_ref = None

for vs in vs_list:
    if vs['destinationAddress'] == ip and vs['destinationPort'] == port:
        vs_ref = vs
        report['devices'].append({'name': vs['deviceReference']['name']})

if report['devices'].__len__() > 0:
    # Retrieve Pool Configuration if the poolReference attribute is present
    if 'poolReference' in vs_ref.keys():
        pool_ref = bigiq.get(vs_ref['poolReference']['link'].replace('localhost', args['host'])).json()
        report['defaultPool'] = pool_ref['name']

        # Get Pool Members
        mem_list = []
        if 'membersCollectionReference' in pool_ref.keys():
            mem_ref = bigiq.get(pool_ref['membersCollectionReference']['link'].replace('localhost', args['host'])).json()
            for mem in mem_ref['items']:
                mem_list.append(mem['name'])
        
        report['defaultPool'] = {'name': pool_ref['name'], 'members': mem_list}

    # Retrieve iRule Configuration if the iRuleReferences attribute is present
    if 'iRuleReferences' in vs_ref.keys():
        ir_list = []
        for ir in vs_ref['iRuleReferences']:
            ir_ref = bigiq.get(ir['link'].replace('localhost', args['host'])).json()
            
            # TCL code is not returned for builtin iRules so we default to blank
            tcl = '' 
            if 'body' in ir_ref.keys():
                tcl = ir_ref['body']
            ir_list.append({'name': ir_ref['name'], 'tcl': tcl})
        report['iRules'] = ir_list

# Print results in json format
print(json.dumps(report, indent=4))