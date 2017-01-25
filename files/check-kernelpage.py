#!/usr/bin/env python
from __future__ import print_function
import sys
import requests
from configparser import ConfigParser
import argparse
import urllib
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
import os
import tarfile,sys
import lzma
import shutil
import subprocess

conf_parser = argparse.ArgumentParser(
    # Turn off help, so we print all options in response to -h
    add_help=False
)
conf_parser.add_argument("-c", "--conf_file",
                         help="Specify config file", metavar="FILE")
args, remaining_argv = conf_parser.parse_known_args()
defaults = {
    "version" : "4.9",
}
if args.conf_file:
    config = ConfigParser()
    config.read([args.conf_file])
    defaults = dict(config.items("Defaults"))

# Don't surpress add_help here so it will handle -h
parser = argparse.ArgumentParser(
    # Inherit options from config_parser
    parents=[conf_parser],
    # print script description with -h/--help
    description=__doc__,
    # Don't mess with format of description
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.set_defaults(**defaults)
parser.add_argument("-version","--version", help="version number", required=True)
args = parser.parse_args(remaining_argv)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

r = requests.get('https://www.kernel.org/')

#print r.status_code
soup = BeautifulSoup(r.content, "lxml")
#print soup
tables = soup.findChildren('table')

# This will get the first (and only) table. Your page may have more.
my_table = tables[2]
#print my_table
tr_table = my_table.findChildren('tr')

def get_version_number(tr_html):
    # get list of td
    tr_html = tr_html.findChildren('td')
    # td 1 contains the kernel number
    tr_html = tr_html[1]
    # get the kernel number inside strong tag
    for node in tr_html.findAll('strong'):
        tr_html_number = ''.join(node.findAll(text=True))
    return tr_html_number

def find_new_version(version_number, argument_version):
    version = version_number.split('.',2)
    try:
        version = version[0] + '.' + version[1]
        if (version == argument_version):
            return version_number
        else:
            pass
    except:
        pass

for i in tr_table:
    version_number=get_version_number(i)
    new_version_revision = find_new_version(version_number, args.version)
    if (new_version_revision != None):
        break
print(new_version_revision)
new_version_split = new_version_revision.split('.',2)
new_version = new_version_split[0] + '.' + new_version_split[1]
print(new_version)


kernel_tarxz = "linux-" + new_version + ".tar.xz"
if (os.path.exists(kernel_tarxz)):
    if (os.path.exists("linux-" + new_version)):
        pass
    else:
        tar = tarfile.open(kernel_tarxz)
        tar.extractall()
        tar.close()
else:
    urllib.request.urlretrieve("http://distfiles.gentoo.org/distfiles/" + kernel_tarxz, kernel_tarxz)
    tar = tarfile.open(kernel_tarxz)
    tar.extractall()
    tar.close()

print(new_version_split)
revision = new_version_split[2]
if ("[EOL]" in revision):
    revision = revision[:-6]
print(revision)
old_revision = int(revision)-1
print(old_revision)
patch_version = new_version + "." + str(old_revision) + "-"+ revision
patch_name = "patch-" + patch_version + ".xz"
patch_url = "http://cdn.kernel.org/pub/linux/kernel/v4.x/incr/"+ patch_name
print(patch_url)
urllib.request.urlretrieve(patch_url, patch_name)
with lzma.open(patch_name) as f, open(patch_name[:-3], 'wb') as fout:
    file_content = f.read()
    fout.write(file_content)

shutil.move(patch_name[:-3],'../linux-patches/'+patch_name[:-3]+'.patch')

cwd = os.getcwd()

bashCommand = "chmod +x patch-kernel.sh"
print(bashCommand)
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print(output)
eprint(error)

bashCommand = "chmod +x ../clean.sh"
print(bashCommand)
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print(output)
eprint(error)

bashCommand = "chmod +x find.sh"
print(bashCommand)
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print(output)
eprint(error)