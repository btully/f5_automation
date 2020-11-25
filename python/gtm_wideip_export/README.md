# GTM WideIP Export

This script exports WideIP name and description fields (type A record only) to a csv file named 'wips.csv' within the current working directory.  
Example output of wips.csv:

```
example1.gslb.acme.com,Description 1
example2.gslb.acme.com,Description 2
```

### Prerequisites


Python - https://www.python.org/

Git CLI Client (not required if downloading from Git website via browser)


### Installing

```
# cd <working directory>
# git clone https://github.com/btully/f5_automation.git
# cd ./f5_automation/python/gtm_wideip_export
# pip install -r requirements.txt
```

### Script Usage
```
# python wideip_export_csv.py -h
usage: wideip_export_csv.py [-h] --host HOST --username USERNAME
                            [--password PASSWORD]

F5 GTM WideIP export (A record type only)

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          BIG-IP IP or Hostname
  --username USERNAME  BIG-IP Username
  --password PASSWORD  BIG-IP Password (Optional)
```

Enter password at prompt
```
# User: admin, enter your password:
```

