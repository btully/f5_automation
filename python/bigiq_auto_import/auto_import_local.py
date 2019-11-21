import json
import sys
import time
import os

# Make sure BIG-IQ is active
try:
    response = os.popen('restcurl -X GET /shared/failover-state').read()
    fo_state = json.loads(response)
    if not (fo_state["nodeRole"] == "STANDALONE" or fo_state["nodeRole"] == "PRIMARY"):
        print("Big-IQ in standby....exiting")
        sys.exit(0)
except:
    print("Failed retrieving device active state")
    sys.exit(1)

# Get Big-IP list
try:
    response = os.popen('restcurl -X GET /cm/system/machineid-resolver').read()
    bigips = json.loads(response)['items']
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
    response = os.popen('restcurl -X POST /cm/global/tasks/device-discovery-import-controller -d \'%s\'' % json.dumps(job_data)).read()
except:
    print("Failed to start device import job")
    sys.exit(1)