from nose.tools import eq_ as eq, assert_raises

import os
from cStringIO import StringIO

from gitosis import ssh
from gitosis.test.util import mkdir, maketemp, writeFile, readFile

def _key(s):
    return ''.join(s.split('\n')).strip()

KEY_1 = _key("""
ssh-rsa +v5XLsUrLsHOKy7Stob1lHZM17YCCNXplcKfbpIztS2PujyixOaBev1ku6H6ny
gUXfuYVzY+PmfTLviSwD3UETxEkR/jlBURACDQARJdUxpgt9XG2Lbs8bhOjonAPapxrH0o
9O8R0Y6Pm1Vh+H2U0B4UBhPgEframpeJYedijBxBV5aq3yUvHkXpcjM/P0gsKqr036k= j
unk@gunk
""")

KEY_2 = _key("""
ssh-rsa 4BX2TxZoD3Og2zNjHwaMhVEa5/NLnPcw+Z02TDR0IGJrrqXk7YlfR3oz+Wb/Eb
Ctli20SoWY0Ur8kBEF/xR4hRslZ2U8t0PAJhr8cq5mifhok/gAdckmSzjD67QJ68uZbga8
ZwIAo7y/BU7cD3Y9UdVZykG34NiijHZLlCBo/TnobXjFIPXvFbfgQ3y8g+akwocFVcQ= f
roop@snoop
""")

class ReadKeys_Test(object):
    def test_empty(self):
        tmp = maketemp()
        empty = os.path.join(tmp, 'empty')
        mkdir(empty)
        gen = ssh.readKeys(keydir=empty)
        assert_raises(StopIteration, gen.next)

    def test_ignore_dot(self):
        tmp = maketemp()
        keydir = os.path.join(tmp, 'ignore_dot')
        mkdir(keydir)
        writeFile(os.path.join(keydir, '.jdoe.pub'), KEY_1+'\n')
        gen = ssh.readKeys(keydir=keydir)
        assert_raises(StopIteration, gen.next)

    def test_ignore_nonpub(self):
        tmp = maketemp()
        keydir = os.path.join(tmp, 'ignore_dot')
        mkdir(keydir)
        writeFile(os.path.join(keydir, 'jdoe.xub'), KEY_1+'\n')
        gen = ssh.readKeys(keydir=keydir)
        assert_raises(StopIteration, gen.next)

    def test_one(self):
        tmp = maketemp()
        keydir = os.path.join(tmp, 'one')
        mkdir(keydir)
        writeFile(os.path.join(keydir, 'jdoe.pub'), KEY_1+'\n')

        gen = ssh.readKeys(keydir=keydir)
        eq(gen.next(), ('jdoe', KEY_1))
        assert_raises(StopIteration, gen.next)

    def test_two(self):
        tmp = maketemp()
        keydir = os.path.join(tmp, 'two')
        mkdir(keydir)
        writeFile(os.path.join(keydir, 'jdoe.pub'), KEY_1+'\n')
        writeFile(os.path.join(keydir, 'wsmith.pub'), KEY_2+'\n')

        gen = ssh.readKeys(keydir=keydir)
        got = frozenset(gen)

        eq(got,
           frozenset([
            ('jdoe', KEY_1),
            ('wsmith', KEY_2),
            ]))

    def test_multiple_lines(self):
        tmp = maketemp()
        keydir = os.path.join(tmp, 'keys')
        mkdir(keydir)
        writeFile(os.path.join(keydir, 'jd"oe.pub'), KEY_1+'\n')

        gen = ssh.readKeys(keydir=keydir)
        got = frozenset(gen)
        eq(got, frozenset([]))

    def test_bad_filename(self):
        tmp = maketemp()
        keydir = os.path.join(tmp, 'two')
        mkdir(keydir)
        writeFile(os.path.join(keydir, 'jdoe.pub'), KEY_1+'\n'+KEY_2+'\n')

        gen = ssh.readKeys(keydir=keydir)
        got = frozenset(gen)

        eq(got,
           frozenset([
            ('jdoe', KEY_1),
            ('jdoe', KEY_2),
            ]))

class GenerateAuthorizedKeys_Test(object):
    def test_simple(self):
        def k():
            yield ('jdoe', KEY_1)
            yield ('wsmith', KEY_2)
        gen = ssh.generateAuthorizedKeys(k())
        eq(gen.next(), ssh.COMMENT)
        eq(gen.next(), (
            'command="/usr/local/bin/gitosis-serve jdoe",no-port-forwarding,no-X11-f'
            +'orwarding,no-agent-forwarding,no-pty %s' % KEY_1))
        eq(gen.next(), (
            'command="/usr/local/bin/gitosis-serve wsmith",no-port-forwarding,no-X11'
            +'-forwarding,no-agent-forwarding,no-pty %s' % KEY_2))
        assert_raises(StopIteration, gen.next)


class FilterAuthorizedKeys_Test(object):
    def run(self, s):
        f = StringIO(s)
        lines = ssh.filterAuthorizedKeys(f)
        got = ''.join(['%s\n' % line for line in lines])
        return got

    def check_no_change(self, s):
        got = self.run(s)
        eq(got, s)

    def test_notFiltered_comment(self):
        self.check_no_change('#comment\n')

    def test_notFiltered_junk(self):
        self.check_no_change('junk\n')

    def test_notFiltered_key(self):
        self.check_no_change('%s\n' % KEY_1)

    def test_notFiltered_keyWithCommand(self):
        s = '''\
command="faketosis-serve wsmith",no-port-forwarding,no-X11-forwardin\
g,no-agent-forwarding,no-pty %(key_1)s
''' % dict(key_1=KEY_1)
        self.check_no_change(s)


    def test_filter_autogeneratedComment_backwardsCompat(self):
        got = self.run('### autogenerated by gitosis, DO NOT EDIT\n')
        eq(got, '')

    def test_filter_autogeneratedComment_current(self):
        got = self.run(ssh.COMMENT+'\n')
        eq(got, '')

    def test_filter_simple(self):
        s = '''\
command="/usr/local/bin/gitosis-serve wsmith",no-port-forwarding,no-X11-forwardin\
g,no-agent-forwarding,no-pty %(key_1)s
''' % dict(key_1=KEY_1)
        got = self.run(s)
        eq(got, '')

    def test_filter_withPath(self):
        s = '''\
command="/foo/bar/baz/gitosis-serve wsmith",no-port-forwarding,no-X11-forwardin\
g,no-agent-forwarding,no-pty %(key_1)s
''' % dict(key_1=KEY_1)
        got = self.run(s)
        eq(got, '')


class WriteAuthorizedKeys_Test(object):
    def test_simple(self):
        tmp = maketemp()
        path = os.path.join(tmp, 'authorized_keys')
        f = file(path, 'w')
        try:
            f.write('''\
# foo
bar
### autogenerated by gitosis, DO NOT EDIT
command="/foo/bar/baz/gitosis-serve wsmith",no-port-forwarding,\
no-X11-forwarding,no-agent-forwarding,no-pty %(key_2)s
baz
''' % dict(key_2=KEY_2))
        finally:
            f.close()
        keydir = os.path.join(tmp, 'one')
        mkdir(keydir)
        writeFile(os.path.join(keydir, 'jdoe.pub'), KEY_1+'\n')

        ssh.writeAuthorizedKeys(
            path=path, keydir=keydir)

        got = readFile(path)
        eq(got, '''\
# foo
bar
baz
### autogenerated by gitosis, DO NOT EDIT
command="/usr/local/bin/gitosis-serve jdoe",no-port-forwarding,\
no-X11-forwarding,no-agent-forwarding,no-pty %(key_1)s
''' % dict(key_1=KEY_1))
