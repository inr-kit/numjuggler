"""
Print out a list using "i" identifiers for inserting and repeating, as in MCNP.

This is for a list of cells, where repititions and multiplication by a constant
are not possible or saldom.

"""


class CustomList(list):
    """
    Methods shortened() and expanded() return a list representation with/without
    'r' and 'i' MCNP notation.

    Constructor takes additionally to the usual list arguments imin and rmin
    arguments.  They define the minimal number of elements to be replaced with
    'Ni' and 'Nr' notation.

    Two methods can be used for check::

        > lorig = [1, 2, 3, .... ]
        > lshrt = list(CustomList(lorig, imin=1, rmin=2).shortened())
        > lexpn = list(CustomList(lshrt).expanded())
        > assert lorig == lexpn

    """ 

    def __init__(self, *args, **kwargs):
        self.__rmin = kwargs.pop('imin', 1) 
        self.__imin = kwargs.pop('rmin', 1)
        super(CustomList, self).__init__(*args, **kwargs)

    @property
    def rmin(self):
        return self.__rmin
    @rmin.setter
    def rmin(self, value):
        self.__rmin = value
    @property
    def imin(self):
        return self.__imin
    @imin.setter
    def imin(self, value):
        self.__imin = value

    def shortened(self):
        """
        Generator of list elements that uses 'Nr' and 'Ni' notation where applicable.
        """

        if len(self) < 2:
            for e in self:
                yield e
        else:
            def _yield():
                if dp == 0:
                    # R-series stops here. x does not belong to it.
                    if n > self.__rmin:
                        yield str(n) + 'r'
                    else:
                        for i in range(n):
                            yield xp
                else:
                    # I-series stops here. x does not belong to it.
                    if n > self.__imin:
                        yield str(n-1) + 'i'
                    else:
                        for i in range(n-1, 0, -1):
                            yield xp - dp*i 
                    yield xp
            xp = self[0]
            dp = self[1] - xp # ensure that the 1-st two elements compose a series. 
            n = 0
            yield xp
            for x in self[1:]:
                d = x - xp
                if d == dp:
                    n += 1
                else:
                    for y in _yield(): yield y
                    n = 1
                xp = x
                dp = d
            for y in _yield(): yield y

    def expanded(self):
        """
        Generator of list elements. If the list contains 'Nr' or 'Ni' notation,
        they are expanded.
        """
        es = None
        for e in self:
            if es != None:
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
                yield e
                ep = e



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

    tr = [ [],
           [1, 2, 2, 2, 1],
           [1, 1, 1, 2],
           [1, 2, 2, 2],
           [1, 2, 3, 4],
           [1, 1, 1, 1],
           [1, 1, 2, 3, 3],
           [1, 1, 2, 3, 3, 4, 5, 5, 5]]

    ti = [ [],
           [1, 3, 4, 5, 7],
           [1, 2, 3, 7, 9],
           [1, 2, 4, 9, 11, 13],
           [1, 2, 4, 7, 7],
           [1, 2, 3],
           [1, 2, 3, 4, 5],
           [1, 2, 3, 3, 4, 5, 6],
           [1, 2, 3, 3, 5, 6, 7, 21, 23, 25]]

    def test_it(tl, func, name):
        print name, '*'*20
        for l in tl:
            print l
            r = func(l)
            print r
            print '-'*10

    def test_CustomList(tl, rmin, imin, name):
        print name, '*'*20
        for l in tl:
            ls = list(CustomList(l, imin=imin, rmin=rmin).shortened())
            le = list(CustomList(ls).expanded())

            if l != le:
                for ll in [l, ls, le]:
                    print '**',
                    for e in ll: print e,
                    print
            else:
                print l, 'passed'
            print '-'*10


    # test_it(tr, shorten_r, 'shorten_r')
    # test_it(ti, shorten_i, 'shorten_i')

    for imin in [1, 2, 3, 4]:
        for rmin in [1, 2, 3, 4]:
            test_CustomList(tr + ti, rmin, imin, 'CustomList imin={}, rmin={}'.format(imin, rmin))

