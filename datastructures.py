# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

"""experimental datastructures"""

from UserDict import DictMixin

class OrderedMultiDict(DictMixin, dict):
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
    # shim
    __key_order = ()

    def __init__(self, arg=None, **kwargs):
        super(OrderedMultiDict, self).__init__()
        self.__key_order = []
        if arg is not None:
            if isinstance(arg, dict):
                self.update(arg)
            else:
                for key, value in arg:
                    self[key] = value
        self.update(kwargs)

    def __delitem__(self, key):
        """Delete the key from the dictionary.

        This removes all values and all keys from the dictionary
        """
        super(OrderedMultiDict, self).__delitem__(key)
        self.__key_order.remove(key)

    def __getitem__(self, key):
        """Fetch the last value set for the given key

        :returns: last set value of the given key
        """
        list_value = super(OrderedMultiDict, self).__getitem__(key)
        return list_value[-1]

    def __iter__(self):
        for k in self.__key_order:
            yield k

    def __setitem__(self, key, value):
        """Set a value for the given key

        This appends the value to an internal list for the provided key,
        creating a new such list if the key previously did not exist in the
        dictionary.  Order of key entry is maintained internally
        """
        try:
            list_value = super(OrderedMultiDict, self).__getitem__(key)
        except KeyError:
            list_value = []
            super(OrderedMultiDict, self).__setitem__(key, list_value)

        list_value.append(value)
        self.__key_order.append(key)

    def getall(self, key):
        """Return all values for a given key

        :returns: list of values
        :rtype: list
        """
        return list(super(OrderedMultiDict, self).__getitem__(key))

    def iteritems(self):
        """Return an iterator over the dictionary's (key, value) pairs

        Unlike dict.iteritems() this will return multiple (key, value) pairs
        for a distinct key if a key was set multiple times. 

        (key,value) pairs are returned in the order they were set.

        :yields: tuples of key value pairs
        """
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
                #  If this is raised, this is an internal consistency issue
                raise RuntimeError("Internal consistency problem with key %s."
                                   "__key_order = %r self=%r" %
                                   (key, self.__key_order, self))
            yield key, value

    def keys(self):
        """Return a copy of the dictionary's list of keys

        Unlike dict.keys(), this returns keys in the order they were set. If a
        key was set multiple times, it will appear multiple times in the result
        list.

        :returns: list of keys
        """
        return list(self.__key_order)

    def pop(self, key, *args):
        """Pop the last value for the given key from the dictionary.

        Unlike dict.pop(), if a key was set multiple times this returns
        each set value in LIFO order.  When there are no more values the
        key is deleted from the dictionary.

        :raises: KeyError if key is not present in the dictionary
        :returns: last set value for the given key
        """
        try:
            list_value = self.getall(key)
            value = list_value.pop(-1)
            if not list_value:
                del self[key]
            return value
        except KeyError:
            # key doesn't exist, so let DictMixin handle default value
            return super(OrderedMultiDict, self).pop(key, *args)
