#!/usr/bin/env python

#
# DNSConf -- GIT-based dns zones management tool
#
# GIT pre-receive hook
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os, sys
import zoneparser, git, dnslib, config


if __name__ == '__main__':
    
    for ref in sys.stdin:
        (old, new, name) = ref.strip().split(' ')

        # do not care about references other than deploy branch
        if name != config.DEPLOY_REF:
            continue

        # validate the changed zonefiles
        zones_ok = True
        for zonefile in dnslib.get_modified_zonefiles(old, new):
            zone_txt = git.content_by_commit_and_name(new, zonefile)
            zone_txt_old = git.content_by_commit_and_name(old, zonefile)
            zone_name = dnslib.file_to_zonename(zonefile)
            zones_ok = zones_ok and dnslib.check_zone(zone_name, zone_txt)
            if dnslib.get_serial(zone_name, zone_txt) <= dnslib.get_serial(zone_name, zone_txt_old):
                print "%s: zonefile changed, but serial was not raised" % zone_name
                zone_ok = False
        if not zones_ok:
            sys.exit(1)

        # everything is alright, let the post-receive hook update DNS server
        sys.exit(0)
