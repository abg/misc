# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

"""dict implementation that preserves key ordering and allows multiple
values per key, which are also in sorted order

>> omdict = OrderedMultiDict()
>> omdict['a'] = '1'
>> omdict['a'] = '2'
>> omdict['a']
2
>> omdict.getall('a')
['1', '2']
>> omdict['b'] = '9'
>> omdict['a'] = '10'
>> for key, value in omdict.iteritems():
...     print key, value
...
a 1
a 2
b 9
a 10
>> def foo(**kwargs):
...     print kwargs
...
>>> foo(**omdict)
{'a': ['1', '2', '10'], 'b': ['9']}
"""

from UserDict import DictMixin

class OrderedMultiDict(DictMixin, dict):
    def __init__(self, arg=None, **kwargs):
        self.__key_order = []

        if arg is not None:
            if isinstance(arg, dict):
                self.update(arg)
            else:
                for key, value in arg:
                    self[key] = value
        self.update(kwargs)

    def __setitem__(self, key, value):
        try:
            list_value = super(OrderedMultiDict, self).__getitem__(key)
        except KeyError:
            list_value = []
            super(OrderedMultiDict, self).__setitem__(key, list_value)

        list_value.append(value)
        self.__key_order.append(key)

    def __getitem__(self, key):
        list_value = super(OrderedMultiDict, self).__getitem__(key)
        return list_value[-1]

    def __delitem__(self, key):
        super(OrderedMultiDict, self).__delitem__(key)
        self.__key_order.remove(key)

    def getall(self, key):
        return super(OrderedMultiDict, self).__getitem__(key)

    def __iter__(self):
        for k in self.__key_order:
            yield k

    def iteritems(self):
        track = {}
        for key in self:
            try:
                i = track[key]
            except KeyError:
                i = iter(self.getall(key))
                track[key] = i

            try:
                value = i.next()
            except StopIteration:
                # XXX: If this is raised, this is an internal consistency issue
                raise RuntimeError("Internal consistency problem with key %s."
                                   "__key_order = %r self=%r" %
                                   (key, self.__key_order, self))
            yield key, value

    def keys(self):
        return list(self.__key_order)

    def pop(self, key, *args):
        try:
            list_value = self.getall(key)
            value = list_value.pop(-1)
            if not list_value:
                del self[key]
            return value
        except KeyError:
            return super(OrderedMultiDict, self).pop(key, *args)

