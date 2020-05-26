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
                ranges, val = ll[1:].split(':', 1)
                ranges = ranges.strip()
                rr = list(_get_map_ranges(ranges))

                # TODO: extract format from val, if val has more than 1 entry
                if '{' in val:
                    val, fmt = val.split('{')
                    fmt = '{' + fmt
                else:
                    fmt = '{:10.3e}'  # default formatting for density
                yield t, rr, val, fmt


def cdens(fname):
    """
    Map file specifies new values of densitites for cells.
    """
    res = OrderedDict()
    resdef = {}
    for t, rr, val, fmt in lines(fname):
        for r in rr:
            res[(t, r)] = float(val), fmt
        # rr can be an empty list that means the default rule
        if len(rr) == 0:
            resdef[t] = float(val), fmt
    return res, resdef
