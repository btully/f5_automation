# LTM Node IP Reporting

This script displays LTM pools and virtual servers that reference a node IP address

EXAMPLE OUTPUT:
```
==============================================================================
Searching for pools and virtual servers that reference node IP - 10.1.20.1
==============================================================================
    
Pool: /Common/example_pool
     -> Virtual: /Common/vs_1
     -> Virtual: /Common/vs_2
```

### Prerequisites


Python - https://www.python.org/

Git CLI Client (not required if downloading from Git website via browser)


### Installing

```
# cd <working directory>
# git clone https://github.com/btully/f5_automation.git
# cd ./f5_automation/python/ltm_node_report
# pip install -r requirements.txt
```

### Script Usage
```
# python node_report.py -h
usage: node_report.py [-h] --host HOST --username USERNAME --node-ip NODE_IP

Query LTM and provide Pool and Virtual Server report based on a Node IP

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          BIG-IP IP or Hostname
  --username USERNAME  BIG-IP Username
  --node-ip NODE_IP    Node IP Address
```

Enter password at prompt
```
# User: admin, enter your password:
```

