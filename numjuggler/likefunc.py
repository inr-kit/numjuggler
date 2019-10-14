# -*- conding: utf-8 -*-

"""
New implementation of mapping, where one can specify
different functions for different ranges and separate values.
"""

from __future__ import print_function
from collections import OrderedDict

from numjuggler.utils.io import resolve_fname_or_stream


def trivial(x):
    """Trivial function returning its argument."""
    return x
# PEP 257: docstring should not be used for function signature. _mydoc
# attribute must contain function expression, with argument denoted as `x`
trivial._mydoc = "x"


def const_func(c):
    """
    Return function f(x) = c.
    """
    def f(x):
        return c
    f._mydoc = '{}'.format(c)
    return f


def add_func(c):
    def f(x):
        return x + c
    f._mydoc = 'x + {}'.format(c)
    return f


class LikeFunctionBase(object):
    """
    Base class for other like-function classes.

    Provides following interface::

        f = LikeFunction(log=True)  # True to log
        y = f(x)                    # f is callable
        print f                     # Defines str(f)
        f.write_log_as_map()        # If logged, outputs results of actual calls

    Children must have the following methods defined:

        get_value(x) -> y

        _str() -> list of strings

    """

    def __init__(self, log=False):
        # Dictionary to log calls
        self.ld = {}

        # Flag to store log
        self.__lf = log

        # Default mapping, applied to elements not in ranges
        self.default = trivial

        # String printed at begin str(self)
        self.doc = ""
        return

    def __call__(self, x):
        res = self.get_value(x)
        if self.log:
            self.ld[x] = res
        return res

    @property
    def log(self):
        return self.__lf

    @log.setter
    def log(self, _log):
        self.__lf = _log

    def __str__(self):
        res = []
        res.extend(self.doc.splitlines())

        res.extend(self._str())

        res.append('other -> {}'.format(self.default._mydoc))
        return '\n'.join(res)

    def write_log_as_map(self, t, fname_or_stream=None):
        if not self.log:
            raise ValueError("Cannon write log for unlogged mapping.")
        with resolve_fname_or_stream(fname_or_stream, "w") as fout:
            for nold, nnew in self.ld.items():
                print('{} {}: {}'.format(t, nnew, nold), file=fout)


class LikeFunction(LikeFunctionBase):
    """
    Gegneral form. Maps separate values or ranges according to their functions.

    Mapping information is in self.mappings, which is an OrderedDict of the
    form `range -> function`.
    """
    def __init__(self, log=False):
        super(LikeFunction, self).__init__(log)

        # OrderedDict of range -> function
        self.mappings = OrderedDict()

        return

    def get_value(self, x):
        for rng, f in reversed(self.mappings.items()):
            if x in rng:
                return f(x)
        return self.default(x)

    def _str(self):
        res = []
        for r, f in self.mappings.items():
            res.append('{} -> {}'.format(r, f._mydoc))
        return res


class LikeIndexFunction(LikeFunctionBase):
    """
    Maps values in a list to its index.

    List to be indexed is in self.vals.
    """
    def __init__(self, log=False, i0=1, skip=[], vals=[]):
        super(LikeIndexFunction, self).__init__(log)

        # List of values to index:
        self.vals = vals

        # First index
        self.i0 = i0

        # Values to skip from indexing and apply default map:
        self.skip = skip

        self.get_value = self.get_valueI
        return

    def unique(self):
        """
        Return only unique entries from vals.
        """
        seen = set()
        seen_add = seen.add
        for x in self.vals:
            if x not in seen:
                seen_add(x)
                yield x

    def compile(self):
        """
        Generate a dictionary x-> vals.index(x), and use this dictionary
        instead of calling index() each time.
        """
        d = {}
        for i, x in enumerate(self.unique()):
            if x in self.skip:
                d[x] = self.default(x)
            else:
                d[x] = i + self.i0
        self.d = d
        self.get_value = self.get_valueD
        return

    def get_valueI(self, x):
        if x not in self.skip:  # and x in self.vals:
            return self.vals.index(x) + self.i0
        else:
            return self.default(x)

    def get_valueD(self, x):
        return self.d[x]

    def _str(self):
        res = []
        for x in self.vals:
            res.append('{} -> {}'.format(x, self.get_value(x)))
        return res


class Range(object):
    """
    Represents a range or a point. Should be considered as immutable.
    """
    def __init__(self, x1, x2=None):
        if x2 is None:
            self.__x1 = x1
            self.__x2 = None
        else:
            x1, x2 = sorted((x1, x2))
            self.__x1 = x1
            self.__x2 = x2
        return

    def __contains__(self, value):
        if self.__x2 is None:
            return value == self.__x1
        else:
            return (self.__x1 <= value <= self.__x2)

    def __str__(self):
        if self.__x2 is None:
            return str(self.__x1)
        else:
            return '[{} -- {}]'.format(self.__x1, self.__x2)

    def __hash__(self):
        return hash((self.__x1, self.__x2))

    def __eq__(self, o):
        return hash(self) == hash(o)

    def __ne__(self, o):
        return hash(self) != hash(o)

# Possible number types:
ntList = ('cel', 'sur', 'u', 'tr', 'mat')

_ntd = dict(map(lambda x: (x[0], x), ntList))


def read_map_file(fname, log=False):
    """
    Read map file and return dictionary of LikeFunction objects.
    """
    # Dictionary type -> LikeFunction
    maps = {}

    with resolve_fname_or_stream(fname, 'r') as mapfile:
        for l in mapfile:
            t, ranges, f = _parse_map_line(l)
            if t is None:
                # l is a comment line
                continue
            if t not in maps:
                m = LikeFunction(log=log)
                m.doc = 'Mappping for `{}` from `{}`'.format(t, fname)
                maps[t] = m
            m = maps[t]
            for r in ranges:
                m.mappings[r] = f
            if not ranges:
                m.default = f
    return maps


def _parse_map_line(l):
    """
    For the map lie returns t, list of ranges and dn.
    """
    # Prepare line and check if not a comment:
    l = l.lower().lstrip()
    if not l or l[0] == '#':
        return None, None, None

    # Number type
    t = _ntd[l[0]]

    rs, os = l[1:].split(':')

    # Allow commas and no spaces in ranges
    rs = rs.replace('--', ' -- ').replace(',', ' ')
    # Use only 1-st entry in the map rule
    os = os.split()[0].lstrip()

    # Sign and dn
    dn = int(os)
    sign = os[0] in '+-'

    ranges = list(_get_map_ranges(rs))

    if sign:
        f = add_func(dn)
    else:
        f = const_func(dn)

    return t, ranges, f


def _get_map_ranges(s):
    tl = (s + ' 0').split()

    v1 = None
    is_range = False
    for t in tl:
        if t == '--':
            is_range = True
        else:
            if is_range:
                yield Range(v1, x2=int(t))
                v1 = None
                is_range = False
            else:
                if v1 is not None:
                    yield Range(v1)
                v1 = int(t)


def get_indices(scards, log=False):
    """
    Return a dict of LikeFunctions to renumber all types by their indices.


    The LikeFuncitons describe mapping for cell, surface, material and universe
    numbers to their indices -- as they appear in the MCNP input file.
    """
    from numbering import get_numbers
    # get list of numbers as they appear in input
    d = get_numbers(scards)

    res = {}
    for k, l in d.items():
        # do not rename universe 0 and material 0
        if k in ('u', 'mat'):
            skip = [0]
        else:
            skip = []
        m = LikeIndexFunction(log=log, i0=1, vals=l, skip=skip)
        m.compile()
        res[k] = m

    return res


if __name__ == '__main__':
    maps = read_map_file('trial_map.txt', log=True)
    for t, m in maps.items():
        print(t)
        print(m)
        for x in range(15):
            print(x, m(x))
        m.write_log_as_map('c')
