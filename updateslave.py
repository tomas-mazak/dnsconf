#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# DNS slave server updater
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import sys, os, subprocess

from config import config


def run_cmd(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    if proc.wait() != 0:
        raise RuntimeError(stdout + '\n' + stderr)
    return stdout.strip()


if __name__ == '__main__':
    os.chdir(config['master']['repo_dir'])
    slave = config['slaves'][sys.argv[1]]
    run_cmd(['/usr/bin/scp', slave['conf'], '%s:%s' % (slave['ssh_host'], slave['conf_dest'])])
    run_cmd(['/usr/bin/ssh', slave['ssh_host'], '/usr/sbin/knotc reload'])
