#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# Post-receive git hook
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import subprocess
import config


def notify_local(command):
    cmd = [command]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    if proc.wait() != 0:
        raise RuntimeError(stdout + '\n' + stderr)
    else:
        print stdout
        print stderr


if __name__ == '__main__':
    
    for server in config.NOTIFY_SERVERS:
        if server.startswith('local:'):
            notify_local(server[len('local:'):])
        else:
            raise NotImplementedError('%s: Server type not supported')
