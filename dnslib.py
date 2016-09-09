#
# DNSConf -- GIT-based dns zones management tool
#
# Zonefiles and DNS server management routines
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os, tempfile, subprocess, datetime, jinja2
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
    return git.staged_files(subtree=config.ZONEDIR)


def get_all_index_zonefiles():
    """
    Get the list of all zonefiles that exist in index
    """
    return git.files_in_index(subtree=config.ZONEDIR)


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


def _update_conf(template, dest, zones):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))

    # master
    template = env.get_template(template)
    zones = [ {'name': z[len(config.ZONEDIR)+1:], 'file': z} for z in sorted(zones) ]
    conf_txt = template.render(zones=zones)
    with open(dest, 'w') as fd:
        fd.write(conf_txt)


def update_namedconf(zones, stage=False):
    """
    Regenerate server configs from templates
    """
    _update_conf(config.NAMEDCONF_MASTER_TPL, config.NAMEDCONF_MASTER, zones)
    _update_conf(config.NAMEDCONF_SLAVE_TPL, config.NAMEDCONF_SLAVE, zones)
    if stage:
        git.stage_file(config.NAMEDCONF_MASTER)
        git.stage_file(config.NAMEDCONF_SLAVE)
