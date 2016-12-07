#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# DNS server updater
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import sys, os
import git, dnslib

from config import config


if __name__ == '__main__':
    os.chdir(config['servers'][sys.argv[1]]['repo_dir'])
    git.pull()
    dnslib.server_reload()
