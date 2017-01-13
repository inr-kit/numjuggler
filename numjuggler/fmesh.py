#!/usr/bin/env python

"""
Analyse fmesh cards.
"""

from numjuggler.parser import Card, are_close_vals


def _get_elements(lst, type_=float):
    """
    return all first elements of lst that can be converted to type_. Remove them
    from lst.
    """
    r = []
    try:
        while lst:
            e = lst.pop(0)
            e = type_(e)
            r.append(e)
    except ValueError:
        lst.insert(0, e)
    return r


def _get_ints(bl):
    """
    For the list of boundaries bl return a shorter bl and ints.

    bl should include the -1st boundary, which in case of geom=xyz is not
    included in ?mesh lists.
    """
    bnew = [bl[0]]
    ints = []
    v0 = bl[0]
    v1 = bl[1]
    d1 = v1 - v0
    i = 1
    for v2 in bl[2:]:
        d2 = v2 - v1
        if are_close_vals(d1, d2, re=1e-6, ra=1e-16):
            i += 1
            v1 = v2
        else:
            ints.append(i)
            bnew.append(v1)
            d1 = v2 - v1
            v0 = v1
            v1 = v2
            i = 1
    ints.append(i)
    bnew.append(v1)
    return bnew, ints


class FmeshCard(Card):
    """
    Adds to the parent class fmesh-specific methods to get fmesh-specific
    parameters.
    """

    def get_values(self):
        """
        Redefine to include call to _analyse
        """
        super(FmeshCard, self).get_values()
        self._analyse()

    def _analyse(self):
        """
        sets attributes.
        """
        tokens = '\n'.join(self.input).replace('=', ' ').lower().split()
        while tokens:
            t = tokens.pop(0)
            if t == 'geom':
                self.geom = tokens.pop(0)
            elif t in ('origin',) or t[1:] in ('mesh',):
                # this should work for emesh, imesh, jmesh, kmesh
                setattr(self, t, tuple(_get_elements(tokens, float)))
            elif t[1:] in ('ints',):
                setattr(self, t, tuple(_get_elements(tokens, int)))
        return

    def ints(self, d=0):
        """
        return ints tuple in direction d. This should be used instead of
        directly accessing ?ints attributes, since they can be undefined.
        """
        iname = 'ijk'[d]
        try:
            return getattr(self, iname + 'ints')
        except AttributeError:
            return (1,) * len(getattr(self, iname + 'mesh'))

    def mesh(self, d=0):
        """
        Similar to ints.
        """
        iname = 'ijk'[d]
        return getattr(self, iname + 'mesh')

    def boundaries(self, d=0):
        """
        d -- one of 0, 1 or 2.
        """
        if self.geom in ('xyz', 'rect'):
            v0 = self.origin[d]
            for n, v1 in zip(self.ints(d), self.mesh(d)):
                d = (v1 - v0)/float(n)
                for i in range(n + 1):
                    yield v0 + d*i
                v0 = v1
