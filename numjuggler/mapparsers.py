# -*- coding: utf-8 -*-

from collections import OrderedDict

from numjuggler.likefunc import _get_map_ranges

# Parsers of map files for different modes

def lines(fname):
    """
    Iterator over meaningful lines in the map file.

    Empty lines and everything after `#` is skipped.
    """
    with open(fname, 'r') as f:
        for l in f:
            ll = l.split('#')[0].strip()
            if ll and ':' in ll:
                ranges, val = ll.split(':')

                # type of ranges
                t, ranges = ranges.split(None, 1)

                # ranges
                rr = list(_get_map_ranges(ranges))
                yield t, rr, val


def cdens(fname):
    """
    Map file specifies new values of densitites for cells.
    """
    res = OrderedDict()
    for t, rr, val in lines(fname):
        for r in rr:
            res[(t, r)] = val
    return res
