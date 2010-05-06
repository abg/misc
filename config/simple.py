# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

"""Parse ini files"""

import re
from datastructures import OrderedMultiDict

# Meant to parse my.cnf files that may have multiple values per key
# inspired by mercurial's awesomely terse config.py
def parse(iterable, include=None):
    sectionre = re.compile(r'\[([^\[]+)\]')
    itemre = re.compile(r'([^=\s]+)\s*(?:(?:=\s*)(.*\S|))?')
    emptyre = re.compile(r'(;|#|\s*$)')
    includere = re.compile(r'!include\s+(\S|\S.*\S)\s*$')
    section = None

    d = OrderedMultiDict()
    for lineno, line in enumerate(iterable):
        m = includere.match(line)
        if m:
            include(m.group(1))
            continue
        if emptyre.match(line):
            continue
        m = sectionre.match(line)
        if m:
            section = m.group(1)
            d.setdefault(section, d.__class__())
            continue
        m = itemre.match(line)
        if m:
            item = m.group(1)
            value = m.group(2)
            d[section][item] = value
            continue
        raise RuntimeError("Parse error. %d: %s" % (lineno + 1, line))
    return d

def read(path):
    return parse(open(path, 'r'), read)
