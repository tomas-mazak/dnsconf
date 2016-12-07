#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# Post-receive git hook
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os, subprocess

from config import config


def notify(command):
    cmd = [command]
    clean_env = {k: os.environ[k] for k in os.environ 
                                  if not k.startswith('GIT_')}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=clean_env)
    (stdout, stderr) = proc.communicate()
    if proc.wait() != 0:
        raise RuntimeError(stdout + '\n' + stderr)
    else:
        print stdout
        print stderr


if __name__ == '__main__':
    
    for name in config['servers']:
        notify(config['servers'][name]['update_cmd'])
