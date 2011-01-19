import os
import re
import codecs
from config4py.datastructures import SortedDict as OrderedDict

class ConfigError(Exception):
    """General error when processing config"""

class ConfigSyntaxError(ConfigError, SyntaxError):
    """Syntax error when processing config"""

class Config(OrderedDict):
    """Simple ini config"""
    section_cre     = re.compile(r'\s*\[(?P<name>[^]]+)\]\s*(?:#.*)?$')
    key_cre         = re.compile(r'(?P<key>[^:=\s\[][^:=]*)=\s*(?P<value>.*)$')
    empty_cre       = re.compile(r'\s*($|#|;)')
    cont_cre        = re.compile(r'\s+(?P<value>.+?)$')
    include_cre     = re.compile(r'%include (?P<name>.+?)\s*$')

    #@classmethod
    def _parse_option(cls, match, optionxform):
        key, value = match.group('key', 'value')
        key = optionxform(key.strip())
        value = value.strip()
        return key, value
    _parse_option = classmethod(_parse_option)

    #@classmethod
    def parse(cls, iterable, optionxform=str):
        """Parse an iterable of lines"""
        cfg = cls()
        section = cfg
        key = None
        for lineno, line in enumerate(iterable):
            if cls.empty_cre.match(line):
                continue
            m = cls.section_cre.match(line)
            if m:
                name = m.group('name')
                #XXX: we throw away cls() if there is an existing
                #     section of the same name (which we will reuse)
                section = cfg.setdefault(name, cls())
                key = None # reset key
                continue
            m = cls.key_cre.match(line)
            if m:
                key, value = cls._parse_option(m, optionxform)
                section[key] = value
                continue
            m = cls.cont_cre.match(line)
            if m:
                if not key:
                    raise ConfigError("unexpected continuation line")
                else:
                    section[key] += line.strip()
                continue
            m = cls.include_cre.match(line)
            if m:
                path = m.group('name')
                if not os.path.isabs(path):
                    base_path = os.path.dirname(getattr(iterable, 'name', '.'))
                    path = os.path.join(base_path, path)
                subcfg = cls.read([path])
                cfg.merge(subcfg)
                continue
            # XXX: delay to end
            raise ConfigSyntaxError("Invalid line",
                                    (getattr(iterable, 'name', '<unknown>'),
                                     0,
                                     lineno,
                                     line))
        return cfg
    parse = classmethod(parse)

    #@classmethod
    def read(cls, iterable, encoding='utf8'):
        """Read a list of paths, load their configs and merge them together"""
        main = cls()
        for path in iterable:
            fileobj = codecs.open(path, 'r', encoding=encoding)
            try:
                cfg = cls.parse(fileobj)
            finally:
                fileobj.close()
            main.merge(cfg)
        return main
    read = classmethod(read)

    def merge(self, config):
        """Merge ``config`` in this config, replacing any existing values"""
        for key, value in config.iteritems():
            if isinstance(value, Config):
                try:
                    section = self[key]
                    if not isinstance(section, Config):
                        # attempting to overwrite a normal key=value with a
                        # section
                        raise TypeError('value-namespace conflict')
                except KeyError:
                    section = self.__class__()
                    self[key] = section
                section.merge(value)
            else:
                self[key] = value

    def meld(self, config):
        """Meld with ``config`` - only adding options that do not already
        exist"""
        for key, value in config.iteritems():
            if isinstance(value, Config):
                try:
                    section = self[key]
                    if not isinstance(section, Config):
                        # attempting to overwrite a normal key=value with a
                        # section
                        raise TypeError('value-namespace conflict')
                except KeyError:
                    section = self.__class__()
                    self[key] = section
                section.meld(value)
            else:
                try:
                    self[key]
                except KeyError:
                    # only add the value if it does not already exist
                    self[key] = value

    def __str__(self):
        """Convert this config to a string"""
        lines = []
        for key, value in self.iteritems():
            if isinstance(value, Config):
                lines.append("[%s]" % key)
                lines.append(str(value))
                lines.append("")
            elif isinstance(value, basestring):
                lines.append("%s = %s" % (key, value))
        return os.linesep.join(lines)
