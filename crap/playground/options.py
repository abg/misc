"""Parse my.cnf files, maintaining section/key order and supporting multiple
values per key in some semi-sane way
"""

import os
import re
from datastructures import OrderedMultiDict

__all__ = [
    'ParseError',
    'parse',
    'stringify',
]

class ParseError(Exception):
    """Raised when there is an error parsing a my.cnf file

    :attribute config: config that would have been returned, were there no
                       parse errors
    :attribute errors: list of SyntaxErrors that were encountered
    """
    def __init__(self, config, errors):
        Exception.__init__(self, config, errors)
        self.config = config
        self.errors = errors


def parse(iterable):
    """Parse an iterable source of lines representing a my.cnf file

    iterable may be a file-like object, a list or a line-yielding generator
    """
    config = OrderedMultiDict()
    itemcre = re.compile(r'(?P<key>\s*[^=\s]+)\s*(?:(?:=\s*)(?P<value>.*\S|))?')
    errors = []
    for line_number, line in enumerate(iterable):
        if line.lstrip().startswith('['):
            section = line.strip()[1:-1].strip()
            config[section] = OrderedMultiDict()
        elif not line.strip():
            continue # skip blank
        elif line.strip()[0] in '#;': # comment characters
            continue # skip comments
        else:
            match = itemcre.match(line)
            if match:
                key, value = match.group('key', 'value')
                section = config.keys()[-1]
                config[section][key] = value and _dequote(value) or value
            else:
                filename = getattr(iterable, 'name', '<unknown>')
                errors.append(SyntaxError('Invalid key-value', (filename, 
                                                                line_number,
                                                                0,
                                                                line)))
    if errors:
        raise ParseError(config, errors)
    return config

def _dequote(value):
    """Remove quotes from a string."""
    if len(value) > 1 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]

    # substitute meta characters per:
    # http://dev.mysql.com/doc/refman/5.0/en/option-files.html
    mysql_meta = {
        'b' : "\b",
        't' : "\t",
        'n' : "\n",
        'r' : "\r",
        '\\': "\\",
        's' : " ",
        '"' : '"',
    }
    return re.sub(r'\\(["btnr\\s])',
                  lambda match: mysql_meta[match.group(1)],
                  value)

def _requote(value):
    """Add quotes to a my.cnf value part of a key/value pair per
    the documentation of MySQL option files"""
    mysql_meta = {
        '\b' : 'b',
        '\t' : 't',
        '\n' : 'n',
        '\r' : 'r',
        '\\' : '\\',
        ' '  : 's',
        '"'  : '"'
    }
    return '"%s"' % re.sub(r'(["\b\t\n\r\\ ])',
                           lambda match: "\\%s" % mysql_meta[match.group(1)],
                           value)

def stringify(config):
    """Convert a cnf dict-like object to a text string"""
    lines = []
    for section in config:
        lines.append('[%s]' % section)
        for key, value in config[section].iteritems():
            if value is None:
                lines.append(key)
            else:
                lines.append("%s = %s" % (key, _requote(value)))
    lines.append('')
    return os.linesep.join(lines)
