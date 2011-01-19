"""This module contains standard checks for Configspec values"""

import csv
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
from subprocess import list2cmdline
from shlex import split

class BaseCheck(object):
    def __init__(self, default=None):
        self.default = default

    def check(self, value, *args, **kwargs):
        """Check a value and return its conversion

        :raises: CheckError on failure
        """
        return value

    def format(self, value):
        """Format a value as it should be written in a config file"""
        return str(value)

class BoolCheck(BaseCheck):
    def check(self, value, **kwargs):
        valid_bools = {
            'yes'  : True,
            'on'   : True,
            'true' : True,
            '1'    : True,
            'no'   : False,
            'off'  : False,
            'false': False,
            '0'    : False,
        }
        value = value or self.default
        return valid_bools[value.lower()]

    def format(self, value):
        return value and 'yes' or 'no'

class FloatCheck(BaseCheck):
    def check(self, value):
        return float(value)

    def format(self, value):
        return "%f" % value

class IntCheck(BaseCheck):
    def check(self, value, min=None, max=None, base=10, default=None):
        return int(value, base)

    def format(self, value):
        return str(value)

class StringCheck(BaseCheck):
    def check(self, value, default=None):
        return value

    def format(self, value):
        return value

class OptionCheck(BaseCheck):
    def check(self, value, *options, **kwargs):
        if value in options:
            return value
        raise ValueError("invalid option %r" % value)

    def format(self, value):
        return str(value)


class ListCheck(BaseCheck):

    #@staticmethod
    def _utf8_encode(unicode_csv_data):
        for line in unicode_csv_data:
            yield line.encode('utf-8')
    _utf8_encode = staticmethod(_utf8_encode)

    def check(self, value, default=None):
        data = self._utf8_encode(BytesIO(value))
        reader = csv.reader(data, dialect='excel', delimiter=',',
                skipinitialspace=True)
        return [cell for row in reader for cell in row ]

    def format(self, value):
        result = BytesIO()
        writer = csv.writer(result, dialect='excel')
        writer.writerow([cell.encode('utf8') for cell in value])
        return result.getvalue().decode('utf8').strip()

class TupleCheck(ListCheck):
    def check(self, value):
        value = super(TupleCheck, self).check(value)
        return tuple(value)


class CmdlineCheck(BaseCheck):
    def check(self, value):
        return [arg.decode('utf8') for arg in split(value.encode('utf8'))]

    def format(self, value):
        return list2cmdline(value)

builtin_checks = (
    ('boolean', BoolCheck),
    ('integer', IntCheck),
    ('float', FloatCheck),
    ('string', StringCheck),
    ('option', OptionCheck),
    ('list', ListCheck),
    ('tuple', TupleCheck),
    ('cmdline', CmdlineCheck),
)
