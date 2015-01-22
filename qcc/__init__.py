# Copyright (c) 2015, Aaron Karper <maergil@gmail.com>

from __future__ import print_function
import random
import os
import functools
import itertools
import sys
from pprint import pprint


def _feed(ff):
    @functools.wraps(ff)
    def wrapped(self, *args, **kwargs):
        args_ = [self._genOrMake(f) for f in args]
        kwargs_ = dict((k, self._genOrMake(f))
                       for k, f in kwargs.items())
        return ff(self, *args_, **kwargs_)
    return wrapped

class Arbitrary(object):
    """Environment for the running of randomized tests.

    """

    def _genOrMake(self, f):
        if callable(f):
            return f(self)
        return f

    def __init__(self, seed=None, size=None, verbose=False):
        """Initializes the random generator."""
        self.random = random.Random(x=seed)
        self.size = size or 256
        self.verbose = verbose or os.environ.has_key('QC_VERBOSE')

    def integers(self):
        """Stream of integers from -2**-size to 2**size

        """
        while True:
            size = 2**self.random.randint(0, self.size)
            yield self.random.randint(-size, size)

    def non_negative(self):
        """Stream of integers from 0 to 2**size

        """
        while True:
            size = 2**self.random.randint(0, self.size)
            yield self.random.randint(0, size)

    def floats(self):
        """Stream of floats from -2**-size to 2**size

        """
        while True:
            size = 2**self.random.randint(0, self.size)
            yield self.random.uniform(-size, size)

    @_feed
    def lists(self, items=integers):
        """Stream of random lists up to len size.

        """
        iter = self._genOrMake(items)
        while True:
            size = self.random.randint(0, self.size)
            yield [next(iter) for _ in xrange(size)]

    @_feed
    def tuples(self, items=integers):
        """Stream of random tuples up to len size.

        """
        return itertools.imap(tuple, self.lists(items))

    @_feed
    def key_value_generator(self, keys=integers, values=integers):
        keys_i, vals_i = keys(self), values(self)
        while True:
            yield (next(keys), next(values))

    @_feed
    def dicts(self, key_values=key_value_generator, keys=None, values=None):
        """Stream of random dicts up to len size.

        """
        if keys is not None and values is not None:
            key_i, val_i = keys(self), values(self)
            key_values = lambda _: itertools.izip(key_i, val_i)

        items = self.lists(key_values)
        while True:
            size = self.random.randint(0, self.size)
            yield dict(next(items) for _ in xrange(size))

    def unicode_chars(self, min=0, max=512):
        """Stream of random unicode characters

        """
        # TODO: Make more elaborate generator
        while True:
            yield unichr(self.random.randint(min, max))

    def chars(self, min=0, max=255):
        """Stream of random characters

        """
        while True:
            yield chr(self.random.randint(min, max))

    def unicodes(self, minunicode=0, maxunicode=512):
        """Stream of random unicode strings

        """
        chars = self.unicode_char(minunicode, maxunicode)
        while True:
            size = self.random.randint(0, self.size)
            yield unicode('').join(next(chars) for _ in xrange(r))

    def strings(self, min=0, max=255):
        """Stream of random strings

        """
        chars = self.char(min, max)
        while True:
            size = self.random.randint(0, self.size)
            yield ''.join(next(chars) for _ in xrange(r))

    @_feed
    def objects(self, _object_class, _fields={}, *init_args, **init_kwargs):
        """Stream of random objects with attributes from dict and constructor
        arguments.

        """
        init_args = [self._genOrMake(f) for f in init_args]
        init_kwargs = dict((k, self._genOrMake(f))
                           for k, f in init_kwargs.iteritems())
        _fields = dict((k, self._genOrMake(f))
                       for k, f in _fields.iteritems())
        while True:
            ctor_args = [next(arg) for arg in init_args]
            ctor_kwargs = dict((k, next(v)) for k, v in init_kwargs.iteritems())
            obj = _object_class(*ctor_args, **ctor_kwargs)
            for k, v in _fields.iteritems():
                setattr(obj, k, next(v))
            yield obj

    def forall(self, tries=100, **kwargs):
        """Decorator for tests to feed randomized arguments.

        """
        def wrap(f):
            @functools.wraps(f)
            def wrapped(*inargs, **inkwargs):
                for _ in xrange(tries):
                    random_kwargs = dict(inkwargs)
                    for name, gen in kwargs.iteritems():
                        random_kwargs[name] = next(gen)
                    try:
                        if self.verbose:
                            pprint(random_kwargs)
                        f(*inargs, **random_kwargs)
                    except:
                        print("Counter example:", file=sys.stderr)
                        pprint(random_kwargs, stream=sys.stderr)
                        raise
            return wrapped
        return wrap

DEFAULT = Arbitrary()

def integers(self=None, *args, **kwargs):
    return (self or DEFAULT).integers(*args, **kwargs)

def non_negative(self=None, *args, **kwargs):
    return (self or DEFAULT).non_negative(*args, **kwargs)

def floats(self=None, *args, **kwargs):
    return (self or DEFAULT).floats(*args, **kwargs)

def lists(self=None, *args, **kwargs):
    return (self or DEFAULT).lists(*args, **kwargs)

def tuples(self=None, *args, **kwargs):
    return (self or DEFAULT).tuples(*args, **kwargs)

def unicode_chars(self=None, *args, **kwargs):
    return (self or DEFAULT).unicode_chars(*args, **kwargs)

def chars(self=None, *args, **kwargs):
    return (self or DEFAULT).chars(*args, **kwargs)

def unicodes(self=None, *args, **kwargs):
    return (self or DEFAULT).unicodes(*args, **kwargs)

def strings(self=None, *args, **kwargs):
    return (self or DEFAULT).strings(*args, **kwargs)

def objects(self=None, *args, **kwargs):
    return (self or DEFAULT).objects(*args, **kwargs)

def forall(self=None, *args, **kwargs):
    return (self or DEFAULT).forall(*args, **kwargs)

__all__ = ['integers', 'floats', 'lists', 'tuples',
           'unicodes', 'characters', 'objects', 'forall',
           'Arbitrary']
