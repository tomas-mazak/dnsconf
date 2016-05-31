#
# DNSConf -- GIT-based dns zones management tool
#
# Zonefile parsing routines
#
# 2016, Tomas Mazak <tomas.mazak@economia.cz>
#

class ZoneParseError(Exception):
    pass

class ZoneParser(object):
    """
    Positional zonefile parser: remembers exact file position of every parsed
    token. Useful for inplace zonefile modification.
    """

    RRTYPES = (
        'A', 'AAAA', 'AFSDB', 'APL', 'CAA', 'CDNSKEY', 'CDS', 'CERT', 'CNAME',
        'DHCID', 'DLV', 'DNAME', 'DNSKEY', 'DS', 'HIP', 'IPSECKEY', 'KEY',
        'KX', 'LOC', 'MX', 'NAPTR', 'NS', 'NSEC', 'NSEC3', 'NSEC3PARAM', 'PTR',
        'RRSIG', 'RP', 'SIG', 'SOA', 'SRV', 'SSHFP', 'TA', 'TKEY', 'TLSA',
        'TSIG', 'TXT'
    )


    def __init__(self, input_data):
        self.data = input_data
        self.pos = 0
        self.owner = None


    def lex_token(self):

        def next(haystack, needle, frm=0):
            pos = haystack.find(needle, frm)
            return pos if pos != -1 else len(haystack)

        # Line beginning with a whitespace and containing any non-whitespace
        # characters is probably a RR with the same owner as the previous RR
        if self.pos < len(self.data) and  self.data[self.pos] in (' ', '\t') \
          and self.pos > 0 and self.data[self.pos-1] == '\n' \
          and self.data[self.pos:next(self.data, '\n', self.pos)].strip() != '':
            self.pos += 1
            return ('', self.pos-1)

        # Skip whitespaces (except \n -- that is a valid token for us)
        while self.pos < len(self.data) and self.data[self.pos] in (' ', '\t'):
            self.pos += 1

        # Detect the end of the string
        if self.pos >= len(self.data):
            return (None, None)

        # Skip comments
        if self.data[self.pos] == ';':
            self.pos = next(self.data, '\n', self.pos)

        # We have a special single-character token
        if self.data[self.pos] in ('\n', '(', ')'):
            self.pos += 1
            return (self.data[self.pos-1], self.pos-1)

        # We have a string token
        frm = self.pos
        while self.pos < len(self.data) and not self.data[self.pos].isspace():
            self.pos += 1

        return (self.data[frm:self.pos], frm)


    def expect_data(self):
        in_multiline = False
        (token, pos) = self.lex_token()
        data = []
        while in_multiline or token not in (None, '\n'):
            if token == '(':
                in_multiline = True
            elif token == ')':
                in_multiline = False
            elif token not in ('\n', ''):
                data.append((token, pos))
            (token, pos) = self.lex_token()
        return data


    def expect_type(self):
        (token, pos) = self.lex_token()

        if token[0].isdigit():
            (token, pos) = self.lex_token()

        if token in ('IN', 'CH'):
            (token, pos) = self.lex_token()

        if token not in self.RRTYPES:
            raise ZoneParseError('Unknown rrtype %s' % token)

        return [token, self.expect_data()]


    def expect_owner(self):
        (token, pos) = self.lex_token()
        while token is not None:

            # Skip special directives
            if len(token) and token[0] == '$':
                while token not in (None, '\n'):
                    (token, pos) = self.lex_token()

            if token == '\n':
                (token, pos) = self.lex_token()
                continue

            if token != '':
                self.owner = token

            return [self.owner] + self.expect_type()

        return None


    def parse_rrs(self):
        rrs = []
        rr = self.expect_owner()
        while rr is not None:
            rrs.append(rr)
            rr = self.expect_owner()
        return rrs


if __name__ == '__main__':

    test_zone="""
$ORIGIN centrum.cz.
$TTL 86400

@       SOA     ns1.centrum.cz. hostmaster.centrum.cz. (
        2015120401 ; Serial (AUTO_INCREMENT)
        21600      ; Refresh
        3600       ; Retry
        604800     ; Expire
        86400 )    ; Negative cache TTL

       NS      ns1.centrum.cz.
       NS      ns2.centrum.cz.

ns1     A       46.255.225.182
ns2     A       93.185.103.191

www     A       46.255.231.48
www2    A       46.255.231.49
www3    A       46.255.231.49
www4    A       46.255.231.49

testme  A       8.8.8.8 ; AUTO_PTR
testme  AAAA    2001::1 ; AUTO_PTR
andme   A       46.255.231.49 ; AUTO_PTR

anotherchange A 11.12.13.14

withttl 3600 A 1.2.3.4
withclass IN A 1.2.3.5
withboth 3600 IN A 1.2.3.6"""

    p = ZoneParser(test_zone)
    print p.parse_rrs()
