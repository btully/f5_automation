import requests
import json
import sys
import time

requests.packages.urllib3.disable_warnings()

BIGIQ_ADDRESS = '56dc1db3-3dc5-4a2c-b023-5da4f5666c64.access.udf.f5.com'
BIGIQ_USER = 'admin'
BIGIQ_PASS = 'admin'
BIGIQ_URL_BASE = 'https://%s/mgmt' % BIGIQ_ADDRESS

# REST resource for BIG-IP that all other requests will use
bigiq = requests.session()
bigiq.verify = False
bigiq.headers.update({'Content-Type' : 'application/json'})

# Get Auth Token
user_data = {"username":BIGIQ_USER, "password":BIGIQ_PASS}
try:
    response = bigiq.post('%s/shared/authn/login' % BIGIQ_URL_BASE, data=json.dumps(user_data))
    if response.status_code != 200:
        print("Invalid login")
        sys.exit()
except:
    print("Connection Unsuccessful")
    sys.exit(1)
else:
    token = response.json()['token']['token']
    bigiq.headers.update({'X-F5-Auth-Token' : token})

# Make sure BIG-IQ is active
try:
    response = bigiq.get('%s/shared/failover-state' % BIGIQ_URL_BASE)
    fo_state = response.json()
    if not (fo_state["nodeRole"] == "STANDALONE" or fo_state["nodeRole"] == "PRIMARY"):
        print("Big-IQ in standby....exiting")
        sys.exit(0)
except:
    print("Failed retrieving device active state")
    sys.exit(1)

# Get Big-IP list
try:
    response = bigiq.get('%s/cm/system/machineid-resolver' % BIGIQ_URL_BASE)
    bigips = response.json()['items']
except:
    print("Failed retrieving managed Big-IP list")
    sys.exit(1)

# Start import job for all Big-IPs
device_details = []
for bip in bigips:
    device_details.append({
       "deviceReference": {
            "link": bip["selfLink"]
        },
        "moduleProperties": [
            { "module": "adc_core" }
        ],
        "conflictPolicy": "USE_BIGIP",
        "versionedConflictPolicy": "USE_BIGIP",
        "deviceConflictPolicy": "USE_BIGIQ"
    })
job_data = { 
    "name": "auto-import-%i" % int(time.time()),
    "deviceDetails": device_details 
}

try:
    response = bigiq.post('%s/cm/global/tasks/device-discovery-import-controller' % BIGIQ_URL_BASE, data=json.dumps(job_data))
except:
    print("Failed to start device import job")
    sys.exit(1)