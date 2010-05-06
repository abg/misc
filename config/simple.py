# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

"""Parse ini files"""

import re

# Meant to parse my.cnf files that may have multiple values per key
# inspired by mercurial's awesomely terse config.py
def parse(iterable, cfgcls=dict, include=None):
    """Parse an iterable source of lines as an ini file and return a dict-like
    object - an instance of cfgclass

    :param iterable: any iterable that provides line-oriented output
                     ex. str.splitlines(), StringIO, open(), etc
    :param cfgcls: dict-like object to use for configs.
                   must have a __setitem__ and setdefault method at minimum
    :param include: method to include other files when a !include[dir] line is
                    encountered

    :returns: instance of cfgcls
    """
    sectionre = re.compile(r'\[([^\[]+)\]')
    itemre = re.compile(r'([^=\s]+)\s*(?:(?:=\s*)(.*\S|))?')
    emptyre = re.compile(r'(;|#|\s*$)')
    includere = re.compile(r'(!include(?:dir)?)\s+(\S|\S.*\S)\s*$')
    section = None

    cfg = cfgcls()
    for lineno, line in enumerate(iterable):
        match = includere.match(line)
        if match:
            include(match.group(2), dir=match.group(1)!='!include')
            continue
        if emptyre.match(line):
            continue
        match = sectionre.match(line)
        if match:
            section = match.group(1)
            cfg.setdefault(section, cfgcls())
            continue
        match = itemre.match(line)
        if match:
            item = match.group(1)
            value = match.group(2)
            cfg[section][item] = value
            continue
        raise RuntimeError("Parse error. %d: %s" % (lineno + 1, line))
    return cfg

def read(path):
    """Read and return a parsed ini file

    :param path: string path to read
    :returns: dict-like object as returned by `parse`
    """
    return parse(open(path, 'r'), read)
