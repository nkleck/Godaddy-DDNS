#!/usr/local/bin/python2.7
#
# this shebang is what works on my pfsense 2.3 fw
#
# Update GoDaddy DNS "A" Record.
# and restart HAProxy
#
# usage: godaddy_ddns.py [-h] hostname.domain.tld
#
# positional arguments:
#   hostname.domain.tld     DNS fully-qualified host name
#
# optional arguments:
#   -h, --help              show this help message and exit
#

import urllib2
import json
import time
import argparse
from subprocess import call

apikey = ''
secret = ''


def get_domain_ip(domain, hostname):
    """get IP of A record from godaddy."""
    url = "https://api.godaddy.com/v1/domains/{}/records/A/{}".format(domain, hostname)
    headers = {'Authorization': 'sso-key {}:{}'.format(apikey, secret),
               'Accept': 'application/json'
               }
    request = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(request)
    if response.getcode() == 200:
        json_data = json.load(response)
        name = json_data[0]['name']
        godaddyIP = json_data[0]['data']
        if name == hostname:
            return godaddyIP
        else:
            print 'godaddy hostname: {} does not match searched hostname: {}'.format(name, hostname)
    else:
        print response.getcode()
        print response.read()


def get_public_ip():
    """get Public IP of network."""
    url = "http://ipv4.icanhazip.com/"
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    pubIP = str(response.read())
    return pubIP.rstrip()


def update_godaddy_record(pubIP, domain, hostname):
    """Update Godaddy A record."""
    data = json.dumps([{"data": pubIP,
                        "ttl": 3600,
                        "name": hostname,
                        "type": "A"
                        }])
    url3 = "https://api.godaddy.com/v1/domains/{}/records/A/{}".format(domain, hostname)
    headers = {'Authorization': 'sso-key {}:{}'.format(apikey, secret),
               'Content-Type': 'application/json',
               'Accept': 'application/json'
               }
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    req = urllib2.Request(url3, headers=headers, data=data.encode('utf-8'))
    req.get_method = lambda:"PUT"
    response3 = opener.open(req)
    print 'status code: {}'.format(response3.getcode())
    print 'If Error: {}\n'.format(response3.read())


parser = argparse.ArgumentParser(description='Update GoDaddy DNS "A" Record.')
parser.add_argument('FQDN', type=str, help='The A Record: host.domain.tld')
args = parser.parse_args()


def main():
    fqdn_list = args.FQDN.split('.')
    if len(fqdn_list) < 3:
        msg = 'FQDN "{}" is not a fully-qualified host name of form "HOST.DOMAIN.TOP"'.format(args.FQDN)
        raise Exception(msg)
    hostname = fqdn_list[0]
    domain = '.'.join(fqdn_list[1:])
    godaddyIP = get_domain_ip(domain, hostname)
    pubIP = get_public_ip()
    if not godaddyIP:
        pass
    if not pubIP:
        print 'There was a problem with http://ipv4.icanhazip.com/'
    else:
        if godaddyIP != pubIP:
            print 'IPs do not match'
            print 'godaddyIP: {}'.format(godaddyIP)
            print 'pubIP: {}'.format(pubIP)
            print '\nUpdating IP with GoDaddy:'
            update_godaddy_record(pubIP, domain, hostname)
            time.sleep(1)
            print '\nChecking if IP was successfully updated...\n'
            time.sleep(2)
            newIP = get_domain_ip(domain, hostname)
            print 'Rechecked, New Godaddy IP = {}\n'.format(newIP)
            print 'Restarting HAProxy\n'
            call(["/usr/local/etc/rc.d/haproxy.sh", "restart"])
        else:
            print 'IPs match! No update needed'
            print 'GodaddyIP: {}'.format(godaddyIP)
            print 'PublicIP:  {}'.format(pubIP)

if __name__ == '__main__':
    main()
