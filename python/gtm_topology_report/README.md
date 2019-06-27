# GTM Topology Reporting

This script provides a topology record report for number of regions per datacenter in JSON format

```
{
    "/Common/DC1": {
        "name": "DC1",
        "regionCount": 3298
    },
    "/Common/DC2": {
        "name": "DC2",
        "regionCount": 7244
    }
}
```

### Prerequisites


Python - https://www.python.org/

Git CLI Client (not required if downloading from Git website via browser)


### Installing

```
# cd <working directory>
# git clone https://github.com/btully/f5_automation.git
# cd ./f5_automation/python/gtm_topology_report
# pip install -r requirements.txt
```

### Script Usage
```
# python topology_report.py -h
usage: topology_report.py [-h] --host HOST --username USERNAME

Query GTM and provide a topology report for number regions per datacenter

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          BIG-IP IP or Hostname
  --username USERNAME  BIG-IP Username
```

Enter password at prompt
```
# User: admin, enter your password:
```

