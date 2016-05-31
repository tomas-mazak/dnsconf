#
# DNSConf -- GIT-based dns zones management tool
#
# YAML config parser
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os
import ConfigParser


# try to find config file in:
# ENV:DNSCONF_CONFIG_FILE, dnsconf.ini, ../dnsconf.ini, /etc/dnsconf.ini
config_file = os.environ.get('DNSCONF_CONFIG_FILE', None)
if config_file is None:
    mydir = os.path.dirname(os.path.realpath(__file__))
    try_files = (os.path.join(mydir, 'dnsconf.ini'),
                 os.path.join(mydir, '..', 'dnsconf.ini'),
                 '/etc/dnsconf.ini')
    for config_file in try_files:
        if os.path.isfile(config_file):
            break

cfg = ConfigParser.ConfigParser()
cfg.read(config_file)

# [common]
ZONEDIR = cfg.get('common', 'zonefile_directory')
DEPLOY_REF = cfg.get('common', 'deploy_ref')

# [remote]
NOTIFY_SERVERS = [ x.strip() for x in cfg.get('remote', 'notify_servers').split(',') ]

# [server]
SERVERTYPE = cfg.get('server', 'server_type')
CONFIG_TEMPLATE = cfg.get('server', 'config_template')
CONFIG_FILE = cfg.get('server', 'config_file')

# [client]
AUTOINCREMENT_SERIAL = cfg.getboolean('client', 'autoincrement_serial')
