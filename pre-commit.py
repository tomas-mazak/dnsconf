#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# GIT pre-commit hook
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os, sys
import git, dnslib, config


if __name__ == '__main__':

    if 'SKIP_HOOKS' in os.environ:
        sys.exit(0)

    # ensure this script is executed from the root directory of current repo
    os.chdir(git.toplevel())

    # validate the changed zones and update serials in index
    zones_ok = True
    modified = dnslib.get_staged_zonefiles()
    for (sha1, fname) in modified:
        zone_txt = git.content_by_sha1(sha1)
        zone_name = dnslib.file_to_zonename(fname)
        zones_ok = zones_ok and dnslib.check_zone(zone_name, zone_txt)

    if not zones_ok:
        sys.exit(1)

    if config.AUTOINCREMENT_SERIAL:
        for (sha1, fname) in modified:
            # update index
            (zone_txt, serial) = dnslib.update_serial(fname, zone_txt)
            git.update_index(fname, zone_txt)

            # update working directory
            with open(fname, 'r') as fd:
                zone_txt = fd.read()
            (zone_txt, serial) = dnslib.update_serial(fname, zone_txt, serial)
            with open(fname, 'w') as fd:
                fd.write(zone_txt)
