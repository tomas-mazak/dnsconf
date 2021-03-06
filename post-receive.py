#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# Post-receive git hook
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os, sys, subprocess
import git

from config import config


def notify(cmd):
    clean_env = {k: os.environ[k] for k in os.environ 
                                  if not k.startswith('GIT_')}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=clean_env,
                                 shell=True)
    (stdout, stderr) = proc.communicate()
    if proc.wait() != 0:
        raise RuntimeError(stdout + '\n' + stderr)
    else:
        print stdout
        print stderr


if __name__ == '__main__':

    for ref in sys.stdin:
        (old, new, name) = ref.strip().split(' ')

        # do not care about references other than deploy branch
        if name != config['common']['deploy_ref']:
            continue

        if config['remote']['notify_servers']:
            changed_files = git.changed_files(old, new)
            print "Updating master with command [%s] ..." % config['master']['update_cmd']
            notify(config['master']['update_cmd'])
            for name in config['slaves']:
                if config['slaves'][name]['conf'] in changed_files:
                    cmd = config['slaves'][name]['update_cmd']
                    print "Updating slave %s with command [%s] ..." % (name, cmd)
                    notify(cmd)
