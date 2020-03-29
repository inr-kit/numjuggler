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
                t = ll[0]  # 1-st entry, c, u, m etc
                ranges, val = ll[1:].split(':')
                ranges = ranges.strip()
                rr = list(_get_map_ranges(ranges))
                yield t, rr, val


def cdens(fname):
    """
    Map file specifies new values of densitites for cells.
    """
    res = OrderedDict()
    resdef = {}
    for t, rr, val in lines(fname):
        for r in rr:
            res[(t, r)] = float(val)
        # rr can be an empty list that means the default rule
        if len(rr) == 0:
            resdef[t] = float(val)
    return res, resdef
