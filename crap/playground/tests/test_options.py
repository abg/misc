from nose.tools import *
from playground.options import parse, stringify, ParseError
from playground import OrderedMultiDict

my_cnf = """# a simple example my.cnf

[mysqld]
datadir = /var/lib/mysql
replicate-wild-do-table = "foo.%"
replicate-wild-do-table = bar.%
innodb_file_per_table

[mysqldump]
single-transaction
ignore-table = foo.bar
ignore-table = foo.baz
ignore-table = foo.biz
ignore-table = foo.boz

"""

def test_parse():
    cfg = parse(my_cnf.splitlines())
    assert_equals(cfg['mysqld']['innodb_file_per_table'], None)
    assert_equals(cfg['mysqld']['replicate-wild-do-table'], 'bar.%')
    assert_equals(cfg['mysqld'].getall('replicate-wild-do-table'),
                  ['foo.%', 'bar.%'])
    assert_equals(cfg['mysqldump'].getall('ignore-table'),
                  ['foo.bar', 'foo.baz', 'foo.biz', 'foo.boz'])

def test_stringify():
    cfg = OrderedMultiDict()
    cfg['mysqld'] = OrderedMultiDict()
    cfg['mysqld']['datadir'] = '/var/lib/mysql'
    cfg['mysqldump'] = OrderedMultiDict()
    cfg['mysqldump']['single-transaction'] = None

    assert_equals(stringify(cfg), '[mysqld]\ndatadir = "/var/lib/mysql"\n[mysqldump]\nsingle-transaction\n')

my_problematic_cnf = """; simple example my.cnf

[mysqld]
; intentionally bad key-value pair
=datadir = foo

; intentionally broken mysqldump section
mysqldump]
    key=value
"""

def test_failures():
    assert_raises(ParseError, parse, my_problematic_cnf.splitlines())
    try:
        parse(my_problematic_cnf.splitlines())
    except ParseError, exc:
        cfg = exc.config
        ok_('mysqld' in cfg)
        assert_equals(len(exc.errors), 1)
    else:
        raise Exception("test_failures() failed to raise expected ParseError")
