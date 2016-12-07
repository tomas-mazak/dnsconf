#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# DNS server updater
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import sys, os, subprocess
import git

from config import config


def server_reload():
    """
    Reload DNS server. Currently BIND9 is supported
    """
    cmd = ['/usr/sbin/rndc', 'reload']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    if proc.wait() != 0:
        raise RuntimeError(stdout + '\n' + stderr)


if __name__ == '__main__':
    os.chdir(config['master']['repo_dir'])
    git.pull()
    server_reload()
