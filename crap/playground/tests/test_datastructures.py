import sys
from nose.tools import *
from playground.datastructures import OrderedMultiDict

def test_is_subclass():
    o = OrderedMultiDict()
    ok_(isinstance(o, dict))

def test_init_from_dict():
    d = { 'foo' : 'bar', 'bar' : 'baz' }
    o = OrderedMultiDict(d)
    assert_equals(o['foo'], 'bar')
    assert_equals(o['bar'], 'baz')

def test_init_from_tuple_seq():
    d = [('foo', 'bar'), ('bar', 'baz')]
    o = OrderedMultiDict(d)
    assert_equals(o['foo'], 'bar')
    assert_equals(o['bar'], 'baz')


def test_del():
    o = OrderedMultiDict(foo='bar', bar='baz')
    ok_('foo' in o)
    ok_('bar' in o)
    assert_equals(len(o), 2)
    del o['foo']
    ok_('foo' not in o)
    ok_('bar' in o)
    assert_equals(len(o), 1)

def test_iteritems():
    values = [
        ('a', '1'),
        ('b', '2'),
        ('c', '3'),
        ('a', '2'),
        ('a', '3'),
    ]
    o = OrderedMultiDict(values)
    assert_equals(o.keys(), [x for x, y in values])
    iterator = o.iteritems()
    assert_equals(iterator.next(), ('a', '1'))
    assert_equals(iterator.next(), ('b', '2'))
    assert_equals(iterator.next(), ('c', '3'))
    assert_equals(iterator.next(), ('a', '2'))
    assert_equals(iterator.next(), ('a', '3'))
    assert_raises(StopIteration, iterator.next)

def test_pop():
    values = [
        ('a', '1'),
        ('b', '2'),
        ('c', '3'),
        ('a', '2'),
        ('a', '3'),
    ]
    o = OrderedMultiDict(values)
    assert_equals(o.pop('a'), '3')
    assert_equals(o.pop('a'), '2')
    assert_equals(o.pop('a'), '1')
    assert_raises(KeyError, o.pop, 'a')

def test_kwargs():
    values = [
        ('a', '1'),
        ('b', '2'),
        ('c', '3'),
        ('a', '2'),
        ('a', '3'),
    ]
    o = OrderedMultiDict()
    for key, value in values:
        o[key] = value
    to_dict = lambda **kwargs: kwargs
    d = to_dict(**o)
    assert_equals(d['a'], ['1','2','3'])
    assert_equals(d['b'], ['2'])
    assert_equals(d['c'], ['3'])
