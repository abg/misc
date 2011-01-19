"""This module provides support for configs that validate other configs"""
from config4py.config import Config
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
            if isinstance(value, Configspec):
                # recurse to section
                value.validate(config[key])
            else:
                name, args, kwargs = CheckParser.parse(value)
                check = self.registry[name](*args, **kwargs)
                config[key] = check.check(config[key])
        return config
