#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# DNS server updater
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os, hashlib, jinja2
import git, dnslib, config


def sha1(txt):
    digest = hashlib.sha1()
    digest.update(txt)
    return digest.digest()


if __name__ == '__main__':

    # ensure this script is executed from the root directory of current repo
    os.chdir(git.toplevel())

    # compute checksum of original config file
    try:
        with open(config.CONFIG_FILE) as f:
            checksum_orig = sha1(f.read())
    except IOError:
        checksum_orig = ''

    # generate new configuration
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(git.toplevel()))
    template = env.get_template(config.CONFIG_TEMPLATE)
    zones = [ {'name': z, 'zonefile': os.path.abspath(z)} for z in sorted(os.listdir(config.ZONEDIR)) ]
    new_config = template.render(zones=zones)
    checksum_new = sha1(new_config)

    # test if the new config differs from original: if so, reload dns server
    if checksum_new != checksum_orig:
        with open(config.CONFIG_FILE, 'w') as f:
            f.write(cnf)
        print "Config file changed, reloading dns server..."
        dnslib.server_reload()
    else:
        print "Config file not changed"
        if config.SERVERTYPE == 'master':
            dnslib.server_reload()
