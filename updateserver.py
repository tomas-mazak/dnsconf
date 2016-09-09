#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# DNS server updater
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os
import git, dnslib, config


if __name__ == '__main__':
    os.chdir(config.SERVER_REPO_DIR)
    git.pull()
    dnslib.server_reload()
