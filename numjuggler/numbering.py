"""
Functions to renumber cells, surfaces, etc. in MCNP input file.
"""
from __future__ import print_function

import warnings
import collections


class _Range(object):
    """
    Represents a range or a point.
    """
    def __init__(self, n1, n2=None):
        if n2 is None:
            self.n1 = n1
            self.n2 = None
        else:
            n1, n2 = sorted((n1, n2))
            self.n1 = n1
            self.n2 = n2
        return

    def __contains__(self, value):
        if self.n2 is None:
            return value == self.n1
        else:
            return (self.n1 <= value <= self.n2)

    def __str__(self):
        if self.n2 is None:
            return str(self.n1)
        else:
            return '[{} -- {}]'.format(self.n1, self.n2)

class LikeFunction(object):
    """
    Class of callables that take two arguments, a number (integer) and a type
    (char or string):

        > f = LikeFunction(d)
        > n_new = f(n_old, 'c')

    This callable is used as a mapping for cell, surface, material, etc numbers
    in an MCNP input file.

    The d argument of the constructor is a dictionary of the following form:

        > d = {}
        > d['c'] = [dn0, rl]

    where dn0 is an integer or callable, and rl is a list of tuples
    representing ranges and mappring on this range, or a dictionary representing
    mapping of separate values. In case rl is a list, its form is:

        > rl = [(n1, m1, dn1), (n1, m2, dn2), ...]

    where n1 and m1 -- are the first and the last elements in the range of
    numbers mapped with respect to dn1. THe dn1 can be an integer or a
    calalble.

    In case rl is a dictionary, its form is:

        > rl = {n1: m1, n2: m2, ...}

    where n1 -- original value that is mapped to m1.

    Mapping dn0 appiled to numbers outside of all ranges in rl. For all dni, if
    it is an integer, the respective mapping is n -> n + dni. If dni is
    callable, the mapping n -> dni(n) is applied.

    """
    def __init__(self, pdict, log=False):
        self.__p = pdict
        self.__lf = log   # flag to log or not.
        self.__ld = {}    # here log is written, if log.

        return

    @staticmethod
    def __applyD(f, n):
        if isinstance(f, collections.Callable):
            return f(n)
        else:
            return f

    @staticmethod
    def __applyL(f, n):
        if isinstance(f, collections.Callable):
            return f(n)
        else:
            return n + int(f)

    def __get_mapping(self, t):
        for key in [t, t[0]]:
            if key in self.__p:
                return self.__p[key]
        else:
            return None, None

    def __call__(self, n, t):
        dn0, param = self.__get_mapping(t)
        if (dn0, param) == (None, None):
            # type not found. Do not apply any mapping
            nnew = n
            # and do not log this mapping
            return n
        elif isinstance(param, dict):
            # param is a dictionary of the form {nold: nnew}
            nnew = param.get(n, dn0)
            nnew = self.__applyD(nnew, n)
        elif isinstance(param, list):
            # param is a list of ranges
            for n1, n2, dn in param:
                if n1 <= n <= n2:
                    nnew = self.__applyL(dn, n)
                    break
            else:
                nnew = self.__applyL(dn0, n)

        if self.__lf:
            ld = self.__ld
            k = (t, nnew)
            if k in ld:
                if ld[k] != n:
                    warnings.warn('Non-injective mapping. ' +
                                  '({}, {}) and ({}, {}) ' +
                                  'are mapped to {}'.format(t, ld[k],
                                                            t, n, nnew))
            else:
                ld[k] = n
        # check that void material not changed:
        if t[0].lower() == 'm' and n == 0 and nnew != 0:
            print('WARNING: material {} replaced with {}.'.format(n, nnew))
            print('Add cell density to the resulting input file.')
        return nnew

    def write_log_as_map(self, fname):
        """
        Writes log to fname in format of map file.
        """
        d = {}
        for t in 'csmut':
            d[t] = {}
        for (t, nnew), n in list(self.__ld.items()):
            d[t[0]][n] = nnew

        with open(fname, 'w') as f:
            for t in 'csmut':
                print('-'*80, file=f)
                for n in sorted(d[t].keys()):
                    nnew = d[t][n]
                    if nnew != n:
                        print('{} {:>6d}:   {:>6d}'.format(t, nnew, n), file=f)


def get_numbers(scards):
    """
    Return dictionary with keys -- number types and values -- list of numbers
    used in the input file.
    """
    r = {}
    for c in scards:
        for v, t in c.values:
            if t not in r:
                r[t] = []
            r[t].append(v)
    return r


def get_indices(scards):
    """
    Return a dictionary that can be used as an argument for the LikeFunction
    class.

    This dictionary describes mapping that maps cell, surface, material and
    universe numbers to their indices -- as they appear in the MCNP input file
    orig.
    """
    # get list of numbers as they appear in input
    d = get_numbers(scards)

    res = {}  # resulting dictionaries of the form number: index
    for t, vl in list(d.items()):
        di = {}
        cin = 1  # all indices start from 1
        for v in vl:
            if v not in di:
                if v != 0:  # v == 0 excluded to skip renumbering of u=0 and m=0
                    di[v] = cin
                    cin += 1
                else:
                    di[v] = 0
        res[t] = di
    return res


def _get_ranges_from_set(nn):
    nnl = sorted(nn)
    if nnl:                         # nnl can be empty
        if [e for e in nn if not isinstance(e, int)]:
            # for float elements of nn only one range, (min, max), is returned
            yield (nnl[0], nnl[-1])
        else:
            n1 = nnl.pop(0)  # start of 1-st range
            np = n1          # previous item
            while nnl:
                n = nnl.pop(0)
                if np in [n-1, n]:
                    # range is continued
                    np = n
                else:
                    yield (n1, np)
                    n1 = n
                    np = n
            yield (n1, np)


def read_map_file(fname):
    """
    Read map file and return functions to be used for mapping.

    Map file format:

        c100--140: +20   # add 20 to cells 100 -- 140
        c150: 151        # replace cell 150 with 151
        c200--300: 400   # add 200 to cells 200 -- 300 (400 without prefix sign means where the new range starts.
        c: 50            # default cell offset. If not specified, it is 0.
    """
    # type short names and accepted types:
    td = {'c': 'cel',
          's': 'sur',
          'u': 'u',
          't': 'tr',
          'm': 'mat'}

    d = {}
    for k in list(td.keys()):
        d[td[k]] = [0, []]  # default dn and list of ranges.
    with open(fname, 'r') as f:
        for l in f:
            ll = l.lower().lstrip()
            if ll and ll[0] in list(td.keys()) and ':' in ll:
                t, ranges, s, dn = _parse_map_line(ll)
                t = td[t]

                if ranges:
                    if not s:
                        dn = dn - ranges[0][0]
                    for n1, n2 in ranges:
                        d[t][1].append((n1, n2, dn))

                else:
                    # default remapping. This is always increment, therefore
                    # sign s is not relevant
                    d[t][0] = dn

                # t = td[ll[0]]
                # rs, os = ll[1:].split(':')
                # rs = rs.replace(' ', '')  # remove spaces from left part
                # os = os.split()[0]        # consider only 1st entry in the right part.
                # if rs == '':
                #     # this is line with default dn. os is always an increment.
                #     d[t][0] = int(os)
                # else:
                #     if '--' in rs:
                #         # there are two entries in the range definition.
                #         n1, n2 = list(map(int, rs.split('--')))
                #     else:
                #         # only one value is given. Means the one-value-range.
                #         n1 = int(rs)
                #         n2 = n1
                #     # in this case, sign matters:
                #     if os[0] in '+-':
                #         dn = int(os)
                #     else:
                #         dn = int(os) - n1
                #     d[t][1].append((n1, n2, dn))
    return d


def _parse_map_line(l):
    """
    For the map lie returns t, list of ranges and dn.
    """
    # range type
    t = l[0]

    rs, os = l[1:].split(':')

    # Allow commas and no spaces in ranges
    rs = rs.replace('--', ' -- ').replace(',' ' ')
    # Use only 1-st entry in the map rule
    os = os.split()[0].lstrip()

    # Sign and dn
    dn = int(os)
    if os[0] in '-+':
        sign = True
    else:
        sign = False

    ranges = list(_get_map_ranges(rs))
    return t, ranges, sign, dn


def _get_map_ranges(s):
    tl = (s + ' 0').split()

    v1 = None
    is_range = False
    for t in tl:
        if t == '--':
            is_range = True
        else:
            if is_range:
                yield v1, int(t)
                v1 = None
                is_range = False
            else:
                if v1 is not None:
                    yield v1, v1
                v1 = int(t)


if __name__ == '__main__':
    pass
