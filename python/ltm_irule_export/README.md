# LTM iRule Export

This outputs an LTM iRule coniguration opbject in JSON format 


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
# python irule_export.py -h
usage: irule_export.py [-h] --host HOST --username USERNAME --irule IRULE
                       [--password PASSWORD]

F5 Big-IP iApp conversion utility

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          BIG-IP IP or Hostname
  --username USERNAME  BIG-IP Username
  --irule IRULE        iRule Name to be exported
  --password PASSWORD  BIG-IP Password (optional)
```

Enter password at prompt
```
# User: admin, enter your password:
```

