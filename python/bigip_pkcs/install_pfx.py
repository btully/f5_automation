import os
import requests
import argparse
import getpass
import json

requests.packages.urllib3.disable_warnings()

def _upload(host, creds, fp):

    chunk_size = 512 * 1024
    headers = {
        'Content-Type': 'application/octet-stream'
    }
    fileobj = open(fp, 'rb')
    filename = os.path.basename(fp)
    if os.path.splitext(filename)[-1] == '.iso':
        uri = 'https://%s/mgmt/cm/autodeploy/software-image-uploads/%s' % (host, filename)
    else:
        uri = 'https://%s/mgmt/shared/file-transfer/uploads/%s' % (host, filename)

    
    size = os.path.getsize(fp)
    start = 0

    while True:
        file_slice = fileobj.read(chunk_size)
        if not file_slice:
            break

        current_bytes = len(file_slice)
        if current_bytes < chunk_size:
            end = size
        else:
            end = start + current_bytes

        content_range = "%s-%s/%s" % (start, end - 1, size)
        headers['Content-Range'] = content_range
        requests.post(uri,
                      auth=creds,
                      data=file_slice,
                      headers=headers,
                      verify=False)

        start += current_bytes

def _extract_pfx_cert(host, creds, filename, password=''):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/util/bash' % (host)
    cmd = 'openssl pkcs12 -in /var/config/rest/downloads/%s -nokeys -out /var/tmp/%s -passin pass:%s' % (filename, str(filename).replace('.pfx', '.crt'), password)
    payload = {
        "command": "run",
        "utilCmdArgs": "-c \'%s\'" % cmd}
    return requests.post(uri, auth=creds, data=json.dumps(payload), headers=headers, verify=False)

def _extract_pfx_key(host, creds, filename, password=''):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/util/bash' % (host)
    cmd = 'openssl pkcs12 -in /var/config/rest/downloads/%s -nocerts -out /var/tmp/%s -passin pass:%s' % (filename, str(filename).replace('.pfx', '.key'), password)
    payload = {
        "command": "run",
        "utilCmdArgs": "-c \'%s\'" % cmd}
    return requests.post(uri, auth=creds, data=json.dumps(payload), headers=headers, verify=False)

def _import_cert(host, creds, filename):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/sys/crypto/cert' % (host)
    payload = {
        'command': 'install',
        'name': filename,
        'from-local-file': '/var/tmp/%s' % filename
    }
    return requests.post(uri, auth=creds, data=json.dumps(payload), headers=headers, verify=False)

def _import_key(host, creds, filename):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/sys/crypto/key' % (host)
    payload = {
        'command': 'install',
        'name': filename,
        'from-local-file': '/var/tmp/%s' % filename
    }
    return requests.post(uri, auth=creds, data=json.dumps(payload), headers=headers, verify=False)

def _save_config(host, creds):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/sys/config' % (host)
    payload = {
        'command': 'save'
    }
    return requests.post(uri, auth=creds, data=json.dumps(payload), headers=headers, verify=False)


def _remove_file(host, creds, filename):
    headers = {
        'Content-Type': 'application/json'
    }
    uri = 'https://%s/mgmt/tm/util/bash' % (host)
    cmd = 'rm -f %s' % filename
    payload = {
        "command": "run",
        "utilCmdArgs": "-c \'%s\'" % cmd}
    return requests.post(uri, auth=creds, data=json.dumps(payload), headers=headers, verify=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload File to BIG-IP')

    parser.add_argument("--host", help='BIG-IP IP or Hostname', required=True)
    parser.add_argument("--username", help='BIG-IP Username', required=True)
    parser.add_argument("--filepath", help='Source PFX Filename with Absolute Path', required=True)
    parser.add_argument("--passphrase", help='PFX passphrase', default='', required=False)
    parser.add_argument('--password', help='BIG-IQ Password (Optional. Otherwise getpass prompted)', required=False)
    args = vars(parser.parse_args())

    hostname = args['host']
    username = args['username']
    filepath = args['filepath']
    filename = filepath.split("/")[-1]
    passphrase = args['passphrase']

    # Setup Password
    if args['password'] != None:
        password = args['password']
    else:
        print('User: %s, enter your password: ' % args['username'])
        password = getpass.getpass()

    # Send file to the BIG-IP.  This script assumes the ILX upload with be a compressed tar file (.tgz)
    _upload(hostname, (username, password), filepath)

    # Extract and import certificate from the pfx file.  Cleanup after import
    certfile = str(filename).replace('.pfx', '.crt')
    _extract_pfx_cert(hostname, (username, password), filename, passphrase)
    _import_cert(hostname, (username, password), certfile)
    _remove_file(hostname, (username, password), '/var/tmp/%s' % certfile)

    # Extract and import key from the pfx file.  Cleanup after import
    keyfile = str(filename).replace('.pfx', '.key')
    _extract_pfx_key(hostname, (username, password), filename, passphrase)
    _import_key(hostname, (username, password), keyfile)
    _remove_file(hostname, (username, password), '/var/tmp/%s' % keyfile)

    # Save Config
    _save_config(hostname, (username, password))
    
    # Clean up uploaded pfx archive 
    _remove_file(hostname, (username, password), '/var/config/rest/downloads/%s' % filename)