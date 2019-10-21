import requests
import argparse
import getpass
import json
import re

requests.packages.urllib3.disable_warnings()

# Globals
HEADERS = { 'Content-Type': 'application/json' }

def get_all_pool_with_members(host, creds):
    # Get all pools 
    pool_url = 'https://%s/mgmt/tm/ltm/pool' % (host)
    result = requests.get(pool_url, auth=creds, headers=HEADERS, verify=False).json()["items"]

    pool_list = []
    for pool in result:
        # Get members subcollection per pool
        pool_string = str(pool['fullPath']).replace('/', '~')
        pool_mem_url = 'https://%s/mgmt/tm/ltm/pool/%s/members' % (host, pool_string)
        members = requests.get(pool_mem_url, auth=creds, headers=HEADERS, verify=False).json()["items"]
        pool_list.append({'name': pool['name'], 'fullPath': pool['fullPath'], 'members': members})
    return pool_list

def get_all_virtuals(host, creds):
    vs_url = 'https://%s/mgmt/tm/ltm/virtual' % (host)
    return requests.get(vs_url, auth=creds, headers=HEADERS, verify=False).json()["items"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query LTM and provide Pool and Virtual Server report based on a Node IP')
    parser.add_argument("--host", help='BIG-IP IP or Hostname', required=True)
    parser.add_argument("--username", help='BIG-IP Username', required=True)
    parser.add_argument("--node-ip", help='Node IP Address', required=True)
    args = vars(parser.parse_args())
    hostname = args['host']

    print("User: %s, enter your password: " % args['username'])
    password = getpass.getpass()
    creds = (args['username'], password)
    node_ip = args['node_ip']

    
    pool_list = get_all_pool_with_members(hostname, creds)
    vs_list = get_all_virtuals(hostname, creds)

    print("""
=============================================================================
Searching for pools and virtual servers that reference node IP - %s
=============================================================================
    """ % node_ip)

    for pool in pool_list:
        match = False
        for member in pool['members']:
            if member['address'] == node_ip:
                match = True
        if match:
            print("Pool: %s" % pool['fullPath'])

            for vs in vs_list:
                if 'pool' in vs.keys() and vs['pool'] == pool['fullPath']:
                    print("     -> Virtual: %s" % vs['fullPath'])
            print ('\n')