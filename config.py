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

_config = parser.as_dict()
config = {}
slaves = {}
for key in _config:
    if key.startswith('slave:'):
        slaves[key[len('slave:'):]] = _config[key]
    else:
        config[key] = _config[key]
config['slaves'] = slaves
config['client']['autoincrement_serial'] = boolean(config['client']['autoincrement_serial'])
config['client']['update_conf'] = boolean(config['client']['update_conf'])
config['remote']['notify_servers'] = boolean(config['remote']['notify_servers'])


if __name__ == '__main__':
    import pprint
    print "Loading configuration from %s ..." % config_file
    print
    pprint.pprint(config)
