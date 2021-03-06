#!/usr/bin/python
import sys
import json
from pprint import pprint
import os.path
import subprocess
import platform
import re

__author__ = 'ostap'


def execute(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if p.returncode != 0:
        print('ERROR: can\'t execute ' + command + '. Error code ' + str(p.returncode))
        print(err)
        exit()
    return out


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
    confstr = '''{
        "RedHat":
    {
        "vhost_file":"vhost.conf",
        "apache": "httpd",
        "apache-root":"/etc/httpd/"
    },
        "CentOS":
    {
        "vhost_file":"vhost.conf",
        "apache": "httpd",
        "apache-root":"/etc/httpd/"
    },
        "Fedora":
    {
        "vhost_file":"vhost.conf",
        "apache": "httpd",
        "apache-root":"/etc/httpd/"
    },
        "Debian":
    {
        "vhost_file":"vhost.conf",
        "apache": "apache2",
        "apache-root":"/etc/apache2/"
    },
        "Ubuntu":
    {
        "vhost_file":"vhost.conf",
        "apache": "apache2",
        "apache-root":"/etc/apache2/"
    },
        "FreeBSD":
    {
        "vhost_file":"vhost.conf",
        "apache": "httpd",
        "apache-root":"/usr/local/etc/apache22/"
    }
}'''
    config_file = 'config.json'
    if os.path.isfile(config_file) is not True:
        distro = linux_distribution()[0]
        config = json.loads(confstr)[distro]
        file = open(config_file, "w")
        json.dump(obj=config, fp=file, sort_keys=True, indent=4)
        file.close()
    else:
        json_data = open(config_file)
        config = json.load(json_data)
        json_data.close()
    return config


def getVhost(path):
    if os.path.isfile(path) is not True:
        pprint('ERROR: no ' + path + ' file. Exiting...')
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


def getApacheConfExtension(apache):
    extension = ''
    out = execute(apache + ' -v')
    m = re.search(' Apache/\d\.(\d)\.\d ', out)
    if m.group(1) >= 4:
        extension = '.conf'
    return extension

if os.geteuid() != 0:
    exit("Please, run script with root privileges. Try sudo")
config = getConfig()
apacheExt = getApacheConfExtension(config['apache'])
vhost = getVhost(config['vhost_file'])
webroot = getWebroot()
sitename = raw_input('Enter site name: ')
# webroot = '/var/www/apache_automation_test/web/'
# sitename = 'apache_automation_test.local'
print('Great! Configuring...')
execute("chmod 777 -R " + webroot)
vhcontent = getVhContent(vhost, webroot, sitename)
createVhostFile(config['apache-root'] + 'sites-available/' + sitename + apacheExt, vhcontent)
execute('a2ensite ' + sitename)
execute('service ' + config['apache'] + ' restart')
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
        subprocess.call('nohup gedit ' + config['apache-root'] + 'sites-available/' + sitename + apacheExt + ' &', shell=True,
                        stdout=f, stderr=f)
else:
    subprocess.call('nano ' + config['apache-root'] + 'sites-available/' + sitename + apacheExt, shell=True)