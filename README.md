# Godaddy DDNS Script for pfSense

## Introduction
This script dynamically udpates GoDaddy DNS A record. I have to use Godaddy for a domain and I wanted a way to update the A record whenever the IP changed.This is particularly useful for home networks hosting websites where the domain is hosted at godaddy. This script uses the godaddy api. You can obtain information here as well as keys https://developer.godaddy.com/. Make sure you generate production keys, do not use the test key/secret.

This script is not ment for @ A records. It only works on FQDN, ie hostname.domain.tld



## Dependencies
I build this with the python libraries already installed on the pfSense (FreeBSD) so I would not have to install any additional libraries in pfsense (Hence urllib2, i prefer requests)

- python2.7
- urllib2
- json

## Usage
godaddy_ddns.py hostname.domain.tld

optionally you can run godaddy_ddns.py -h for these same instructions.

## Cron It!
Obviously you do not want to have to run this script every time the IP changes. Thats what cron is for. You can try it cmd line with crontab -e, Or you can go the easy way and install the Cron pkg in pfSense. Once the package is installed, upload your script to your pfSense box (and remember where you placed it). Then schedule your cron job. Below is a sample cron job:


2	\*	\*	\*	\*	root	/usr/local/bin/python2.7 /home/<your user>/godaddy-ddns.py hostname.domain.tld


## HAProxy
Final note, I use HAProxy and noticed that when my IP changed, HAProxy saw the new IP attached to my WAN, but would not allow connections until HAProxy was reloaded. This script reloads HAProxy. If you do not need that function, you can remove line 108.

There is a checkbox 'Reload behaviour' in HAProxy that may do this function. I have not tested, as my IP hasnt changed at the time of this writing. 
