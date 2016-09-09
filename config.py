#
# DNSConf -- GIT-based dns zones management tool
#
# INI config parser
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#


import os
import ConfigParser


class DictParser(ConfigParser.ConfigParser):
    """
    Parse the provided ini file into a python dict
    """
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d


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

def boolean(string):
    if isinstance(string, bool):
        return string
    elif string.lower() in ('yes', 'true', '1'):
        return True
    elif string.lower() in ('no', 'false', '0'):
        return False
    else:
        raise ValueError('%s is not a valid booelan value')


parser = DictParser()
parser.read(config_file)
cfg = parser.as_dict()


# [common]
common = cfg.get('common', {})
ZONEDIR = common.get('zonefile_directory', 'zones')
REMOTE_REF = common.get('remote_ref', 'refs/remotes/origin/master')
DEPLOY_REF = common.get('deploy_ref', 'refs/heads/master')
NAMEDCONF_MASTER = common.get('namedconf_master', None)
NAMEDCONF_SLAVE = common.get('namedconf_slave', None)

# [client]
client = cfg.get('client', {})
AUTOINCREMENT_SERIAL = boolean(client.get('autoincrement_serial', False))
UPDATE_NAMEDCONF = boolean(client.get('autoincrement_serial', False))
NAMEDCONF_MASTER_TPL = client.get('namedconf_master_tpl', None)
NAMEDCONF_SLAVE_TPL = client.get('namedconf_slave_tpl', None)

# [remote]
#NOTIFY_SERVERS = [ x.strip() for x in cfg.get('remote', 'notify_servers').split(',') ]

# [server]
server = cfg.get('server', {})
SERVER_REPO_DIR = server.get('repo_dir', None)
#SERVERTYPE = cfg.get('server', 'server_type')
#CONFIG_TEMPLATE = cfg.get('server', 'config_template')
#CONFIG_FILE = cfg.get('server', 'config_file')
