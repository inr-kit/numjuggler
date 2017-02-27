"""
Print out a list using "i" identifiers for inserting and repeating, as in MCNP.

This is for a list of cells, where repititions and multiplication by a constant
are not possible or saldom.

"""

from __future__ import print_function


def shorten(list_, rmin=2, imin=2):
    """
    Generator of list elements that uses 'Nr' and 'Ni' notation where
    applicable.
    """

    if len(list_) < 2:
        for e in list_:
            yield e
    else:
        def _yield():
            if dp == 0:
                # R-series stops here. x does not belong to it.
                if n > rmin:
                    yield str(n) + 'r'
                else:
                    for i in range(n):
                        yield xp
            else:
                # I-series stops here. x does not belong to it.
                if n > imin:
                    yield str(n-1) + 'i'
                else:
                    for i in range(n-1, 0, -1):
                        yield xp - dp*i
                yield xp
        xp = list_[0]
        dp = list_[1] - xp  # ensure that 1st two elements compose a series.
        n = 0
        yield xp
        for x in list_[1:]:
            d = x - xp
            if d == dp:
                n += 1
            else:
                for y in _yield():
                    yield y
                n = 1
            xp = x
            dp = d
        for y in _yield():
            yield y


def expand(list_):
    """
    Generator of list elements. If the list contains 'Nr' or 'Ni' notation,
    they are expanded.
    """
    es = None
    for e in list_:
        if es is not None:
            e = float(e)
            d = (e - es) / (n+1)
            for i in range(1, n+2):
                yield es + d*i
            es = None
            ep = e
        elif 'r' in str(e).lower():
            n = int(e[:-1])
            for i in range(n):
                yield ep
        elif 'i' in str(e).lower():
            n = int(e[:-1])
            es = ep
        else:
            ep = float(e)
            yield ep


if __name__ == '__main__':
    # test cases should cover the following situations:
    # * empty list
    # * only inside
    # * only at begin
    # * only at end
    # * list with no changes
    # * all list
    # * at begin and at end
    # * at begin, inside and end

    tr = [[],
          [1, 2, 2, 2, 1],
          [1, 1, 1, 2],
          [1, 2, 2, 2],
          [1, 2, 3, 4],
          [1, 1, 1, 1],
          [1, 1, 2, 3, 3],
          [1, 1, 2, 3, 3, 4, 5, 5, 5]]

    ti = [[],
          [1, 3, 4, 5, 7],
          [1, 2, 3, 7, 9],
          [1, 2, 4, 9, 11, 13],
          [1, 2, 4, 7, 7],
          [1, 2, 3],
          [1, 2, 3, 4, 5],
          [1, 2, 3, 3, 4, 5, 6],
          [1, 2, 3, 3, 5, 6, 7, 21, 23, 25]]

    def test_(tl, rmin, imin, name):
        print(name, '*'*20)
        for l in tl:
            ls = list(shorten(l, imin=imin, rmin=rmin))
            le = list(expand(ls))

            if l != le:
                for ll in [l, ls, le]:
                    print('**', end=' ')
                    for e in ll:
                        print(e, end=' ')
                    print()
                    print('-'*10)

    for imin in [1, 2, 3, 4]:
        for rmin in [1, 2, 3, 4]:
            test_(tr + ti, rmin, imin,
                  'CustomList imin={}, rmin={}'.format(imin, rmin))
