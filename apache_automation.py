#!/usr/bin/python
import sys
import json
from pprint import pprint
import os.path
import subprocess
import platform

__author__ = 'ostap'

def setConfig():
    pprint('NOT IMPLEMENTED')
    exit()


def linux_distribution():
    try:
        return platform.linux_distribution()
    except:
        print('ERROR: this script is for linux only. Exitting...')
        exit()


def getConfig():
    config_file = 'config.json'
    if os.path.isfile(config_file) is not True:
        print('ERROR: config.json file not found. Exitting...')
        exit()
    json_data = open(config_file)
    config = json.load(json_data)
    json_data.close()
    distro = linux_distribution()[0]
    return config[distro]


def getVhost(path):
    if os.path.isfile(path) is not True:
        pprint('ERROR: no vhost.conf file. Exiting...')
        exit()
    f = open(path)
    vhost = f.read()
    f.close()
    return vhost


def createVhostFile(path, content):
    if os.path.isfile(path):
        print('ERROR: vhost file ' + path + ' already exists. Exiting...')
        exit()
    file = open(path, "w")
    file.write(content)
    file.close()
    return True


def getVhContent(vhost, documentroot, servername):
    content = vhost.replace('{-SERVER_NAME-}', servername)
    content = content.replace('{-DOCUMENT_ROOT-}', documentroot)
    return content


def hostExists(hostname):
    """ str -> bool
    The exists function opens the host file and checks to see if the hostname requested exists in the host file.
    It opens the host file, reads the lines, and then a for loop checks each line to see if the hostname is in it.
    If it is, True is returned. If not, False is returned.
    :param hostname:
    :return:
    """
    if 'linux' in sys.platform:
        filename = '/etc/hosts'
    else:
        filename = 'c:\windows\system32\drivers\etc\hosts'
    f = open(filename, 'r')
    hostfiledata = f.readlines()
    f.close()
    for item in hostfiledata:
        if hostname in item:
            return True
    return False


def updateHost(ipaddress, hostname):
    """
    The update function takes the ip address and hostname passed into the function and adds it to the host file.
    :param ipaddress:
    :param hostname:
    """
    if 'linux' in sys.platform:
        filename = '/etc/hosts'
    else:
        filename = 'c:\windows\system32\drivers\etc\hosts'
    outputfile = open(filename, 'a')
    entry = "\n" + ipaddress + "\t" + hostname + "\n"
    outputfile.writelines(entry)
    outputfile.close()


def getWebroot():
    webroot = raw_input('Enter webroot path: ')
    while os.path.isdir(webroot) is not True:
        webroot = raw_input('ERROR: Enter valid webroot path: ')
    if webroot[-1:] != '/':
        webroot += '/'
    return webroot

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
config = getConfig()
vhost = getVhost(config['vhost_file'])
webroot = getWebroot()
sitename = raw_input('Enter site name: ')
# webroot = '/var/www/apache_automation_test/web/'
# sitename = 'apache_automation_test.local'
print('Great! Configuring...')

with open(os.devnull, "w") as f:
    res = subprocess.call("chmod 777 -R " + webroot, shell=True, stdout=f, stderr=f)
if res != 0:
    print('ERROR: can\'t execute chmod 777 -R ' + webroot + '. Exiting...')
    exit()

vhcontent = getVhContent(vhost, webroot, sitename)
createVhostFile(config['apache-root'] + 'sites-available/' + sitename + '.conf', vhcontent)

with open(os.devnull, "w") as f:
    res = subprocess.call('a2ensite ' + sitename, shell=True, stdout=f, stderr=f)
if res != 0:
    print('ERROR: can\'t execute a2ensite ' + sitename + '. Exiting...')
    exit()

with open(os.devnull, "w") as f:
    res = subprocess.call('service ' + config['apache'] + ' restart', shell=True, stdout=f, stderr=f)
if res != 0:
    print('ERROR: can\'t execute service ' + config['apache'] + ' restart. Exiting...')
    exit()

if hostExists(sitename) is False:
    updateHost('127.0.0.1', sitename)
else:
    print('WARNING: host ' + sitename + ' already exists')

print('CONGRATULATIONS!')
print('Site ' + sitename + ' is running')
print('Webroot is ' + webroot)

with open(os.devnull, "w") as f:
    res = subprocess.call('which gedit', shell=True, stdout=f, stderr=f)
if res == 0:
    with open(os.devnull, "w") as f:
        subprocess.call('nohup gedit ' + config['apache-root'] + 'sites-available/' + sitename + '.conf &', shell=True, stdout=f, stderr=f)
else:
    with open(os.devnull, "w") as f:
        subprocess.call('nano ' + config['apache-root'] + 'sites-available/' + sitename + '.conf &', shell=True, stdout=f, stderr=f)