# Big-IQ Virtual Server Reporting

This script queries Big-IQ to provide a Big-IP Virtual Server configuration report in JSON format.  Configuration items reported:
* BIG-IP Devices
* Default Pool and Members
* iRules

Sample Output
```
{
    "target": {
        "ip": "10.1.10.200",
        "port": "8088"
    },
    "devices": [
        {
            "name": "BOS-vBIGIP02.termmarc.com"
        },
        {
            "name": "BOS-vBIGIP01.termmarc.com"
        }
    ],
    "defaultPool": {
        "name": "MyAppPool",
        "members": [
            "MyAppNode1:80",
            "MyAppNode2:80"
        ]
    },
    "iRules": [
        {
            "name": "log_http",
            "tcl": "when HTTP_REQUEST {\n    log local0. \"Requested hostname: [HTTP::host] from IP: [IP::local_addr]\"\n}"
        }
    ]
}
```

### Prerequisites


Python - https://www.python.org/

Git CLI Client (not required if downloading from Git website via browser)


### Installing

```
# cd <working directory>
# git clone https://github.com/btully/f5_automation.git
# cd ./f5_automation/python/bigiq_vs_report
# pip install -r requirements.txt
```

### Script Usage
```
# python vs_report.py -h
usage: vs_report.py [-h] --host HOST --username USERNAME --vip VIP
                    [--auth-provider AUTH_PROVIDER] [--password PASSWORD]

F5 Big-IQ Virtual Server Report Utility

arguments:
  -h, --help                    show this help message and exit
  --host HOST                   BIG-IQ IP or Hostname
  --username USERNAME           BIQ-IQ Username
  --vip VIP                     IP address and Port of the BigIP virtual server. Ex. '10.1.10.200:443'
  --auth-provider AUTH_PROVIDER BIG-IQ External Auth Provider name (Optional. Default is local auth: "tmos")
  --password PASSWORD           BIG-IQ Password (Optional. Otherwise getpass prompted)
```

Enter password at prompt
```
# User: <username>, enter your password:
```