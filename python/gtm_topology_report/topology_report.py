import requests
import argparse
import getpass
import json
import re

requests.packages.urllib3.disable_warnings()

def get_datacenters(host, creds):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/gtm/datacenter' % (host)

    result = requests.get(uri, auth=creds, headers=headers, verify=False)
    return result.json()["items"]

def get_topo_records(host, creds):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/gtm/topology' % (host)

    result = requests.get(uri, auth=creds, headers=headers, verify=False)
    return result.json()["items"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Query GTM and provide a topology report for number regions per datacenter')
    parser.add_argument("--host", help='BIG-IP IP or Hostname', required=True)
    parser.add_argument("--username", help='BIG-IP Username', required=True)
    args = vars(parser.parse_args())
    hostname = args['host']

    print("User: %s, enter your password: " % args['username'])
    password = getpass.getpass()
    creds = (args['username'], password)

    # Get Datacenters from GTM 
    dc_list = get_datacenters(hostname, creds)

    # Get Topology Records from GTM
    topo_list = get_topo_records(hostname, creds)

    # Initialize topology record tracker and set count to 0 for each dc
    topo_rec_tracker = {}
    for dc in dc_list:
        topo_rec_tracker[dc["fullPath"]] = { "name": dc["name"], "regionCount": 0 }

    # Iteriate through the topology record list to populate record tracker
    for tr in topo_list:
        # Perform a regular expression search to see if the topology record references a datacenter
        dc_search = re.search(r'datacenter\s+(\S+)$', tr["name"])
        
        # If datacenter found increment the topo rec tracker for that dc
        if (dc_search):
            dc_full_path = dc_search.group(1)

            # Increment dc record tracker
            topo_rec_tracker[dc_full_path]["regionCount"] += 1

    # Print results in json format
    print(json.dumps(topo_rec_tracker, indent=4, sort_keys=True))