"""This module provides support for configs that validate other configs"""
from config4py.config import Config
from config4py.parsing import CheckParser
from config4py.checks import builtin_checks

class Configspec(Config):
    """A configuration that can validate other configurations
    """
    def __init__(self, *args, **kwargs):
        super(Configspec, self).__init__(*args, **kwargs)
        self.registry = dict(builtin_checks)

    def validate(self, config):
        """Validate a config against this configspec"""
        for key, value in self.iteritems():
            #XXX: value must be a Configspec if we want
            #     to recurse to more than 1 level
            if isinstance(value, dict):
                # recurse to section
                try:
                    cfgsect = config[key]
                except KeyError:
                    cfgsect = config.setdefault(key, config.__class__())
                value.validate(cfgsect)
            else:
                name, args, kwargs = CheckParser.parse(value)
                check = self.registry[name](*args, **kwargs)
                try:
                    value = config[key]
                except KeyError:
                    value = kwargs.get('default')
                config[key] = check.check(value)
        return config
