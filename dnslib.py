#
# DNSConf -- GIT-based dns zones management tool
#
# Zonefiles and DNS server management routines
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os, tempfile, subprocess, datetime
import git, zoneparser, config


def file_to_zonename(filename):
    """
    Get the zone name based on zonefile file name
    """
    zdir = os.path.join(config.ZONEDIR,'')
    return filename[len(zdir):]


def get_modified_zonefiles(old, new):
    """
    Get the list of zones modified between the two given commits
    """
    zdir = os.path.join(config.ZONEDIR,'')
    return [f for f in git.changed_files(old, new) if f.startswith(zdir)]


def get_staged_zonefiles():
    """
    Get the list of zones modified in index (staged)
    """
    zdir = os.path.join(config.ZONEDIR,'')
    return [(sha1, f) for (sha1, f) in git.staged_files() if f.startswith(zdir)]


def check_zone(name, zone_txt):
    """
    Check for syntax errors
    """
    with tempfile.NamedTemporaryFile('w') as tmp:
        tmp.write(zone_txt)
        tmp.flush()
        cmd = ['named-checkzone', name, tmp.name]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        if proc.wait() != 0:
            print stderr
            print stdout
            return False
        else:
            return True


def server_reload():
    """
    Reload DNS server. Currently BIND9 is supported
    """
    cmd = ['rndc', 'reload']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    if proc.wait() != 0:
        raise RuntimeError(stdout + '\n' + stderr)
        

def increment_serial(old_value):
    """
    Get the standard format zone serial for the current date (YYYYMMDD01)
    """
    d = datetime.date.today()
    today_lowest = ((d.year * 100 + d.month) * 100 + d.day) * 100 + 1
    return max(today_lowest, old_value+1)


def get_serial(name, zone_txt):
    """
    Get the SOA serial and its position in the given zone
    """
    if not name.endswith('.'):
        name = name + '.'

    parser = zoneparser.ZoneParser(zone_txt)
    rrs = parser.parse_rrs()

    for (owner, rrtype, data) in rrs:
        if owner in ('@', name) and rrtype == 'SOA':
            (value, pos) = data[2]
            return (int(value), pos)


def update_serial(fname, zone_txt, serial=None):
    """
    Update the serial in zone in-place
    """
    name = file_to_zonename(fname)

    if serial == None:
        last_version = git.head_version(fname)
        if last_version is None:
            last_version = zone_txt
        last_serial = get_serial(name, last_version)[0]
        serial = increment_serial(last_serial)

    (toreplace, pos) = get_serial(name, zone_txt)

    new_txt = zone_txt[:pos] + str(serial) + zone_txt[pos+len(str(toreplace)):]

    return (new_txt, serial)
