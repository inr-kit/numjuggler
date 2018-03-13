from math import copysign


def areclose(l, rtol=1e-4, atol=1e-7, cmnt=None, name=''):
    """
    Check if all elements in the list l are close to each other.

    Implementation originally based on numpy.isclose formula
    """
    f1 = '{}'
    f2 = '{:15.8e}'

    A = min(l)
    B = max(l)
    if atol is None:
        ares = False
        astr = f1.format(atol)
    else:
        ares = B - A <= atol
        astr = f2.format(atol)
    if rtol is None:
        rres = False
        rstr = f1.format(rtol)
    else:
        b = max(map(abs, l))
        rres = B - A <= rtol*b
        rstr = f2.format(rtol*b)

    result = ares or rres

    if cmnt is not None:
        # assume it is a list of comments. Add here information
        c = cmnt.append
        if name:
            c('c     Are close check: ' + name + ': {}'.format(result))
        else:
            c('c     values: ' + ' '.join('{:15.8e}'.format(v) for v in l))
            c('c     B:      {:15.8e}'.format(B))
            c('c     A:      {:15.8e}'.format(A))
            c('c     B - A:  {:15.8e}'.format(B - A))
            c('c     atol:   ' + astr)
            c('c     rtol*b: ' + rstr)
            c('c     check result: {}'.format(result))
    return result


def get_params(card):
    """
    Return parameters of the GQ card.
    """
    p1, p2 = card.lower().split('gq')
    # Check if there is transformation:
    tr = len(p1.split()) > 1
    return tr, map(float, p2.split())


def get_cone_or_cylinder(pl):
    """
    Components of the cone/cylinder axis, xn, yn and zn, can be defined from
    the equations for A, B and C. For a cone, these equations can also be used
    to define the cone angle.

    For a cylinder,

    Coefficients D, E and F also depend on the cone angle and xn, yn, zn. These
    equations are used to check if the set A -- K describes a cone/cylinder.
    """

    # If parameters pl are exact and represent a cylinder, t2 is 0. If pl
    # represent a cone, r2 is 0. Thus, without rounding errors, the criteria
    # for cylinder:
    #
    #   t2 = 0
    #   pl are consistent for cylinder
    #
    # and criteria for cone:
    #
    #   r2 = 0
    #   pl are consistenr for cone.
    #
    # Values in pl, however, undergo rounding errors, therefore the above
    # criteria fail (not met although pl represents cylinder or cone).  r2 for
    # cone cannot be defined if t2 is close to 0, since it is in denominator,
    # therefore the cone parameters can be defined only when t2 is above some
    # positive threshold. Consistency checks for cylinder and cone are equal
    # (conditin onto the sum A+B+C that is different for cone and cylinder, is
    # used already above as t^2 = 0):
    #
    #   A <= 1
    #   B <= 1
    #   C <= 1
    #   D^2(1 - C)  =  E^2(1 - A)  =  F^2(1 - B)
    #
    #
    # If for some chosen e1, 0 <= t2 < e1, equations for cone are not applied.
    # in this case, parameters for cylinder are calculated for adjusted A, B and
    # C. Additional check is done for the cylinder's radius: if it is below some
    # e2, a warning message is printed.
    #
    # If e1 <= t2, parameters for cone can be evaluated. If t2 is still small,
    # i.e. t2 < e3 for some e3 (e1 < e3), parameters for both, cylinder and cone
    # are computed. A, B and C are adjusted for cylinder and cone separately.
    # The choise between cone and cylinder is done by comparing r2 for
    # adjusted input parameters. If r2 for cylinder is below e4 (can be equal to
    # e2 used for warning above), the cylinder must be cast away. If r2 for cone
    # is above e5, the cone must be cast away. When only one choice remains, it
    # is printed out. When no choices remains, GQ not converted. When both
    # choices remain, cylinder is xhosen as a more simple one and a warning
    # message is printed.

    # If e3 < t2, only cone is considered. Parameters for cone are calculated
    # for adjusted A, B and C.
    #
    # In all cases of t2 value considered above, consistency check for D, E and
    # F is performed (consistency checks for A, B and C are useless, since they
    # are adjusted to meet them). If consistency check fails, the cossespondent
    # option (cone or cylinder) is cast away.

    et1 = 1e-7  # for t2 below, only cylinder is considered
    et2 = 1e-3  # for t2 above, only cone is considered
    er1 = 1e-3  # for cylinder's r2 below, warning is printed
    er2 = 1e-3  # Cylinder with r2 below is cast away
    er3 = 1e-3  # Cone with r2 above is cast away
    ecca, eccr = 1e-6, 1e-5  # abs. and rel. tolerances for consistency checks

    A, B, C = pl[0:3]
    t2 = sum((2.0, -A, -B, -C))

    cmnt = []
    c = cmnt.append
    c('c Cylinder/cone parameters from GQ: ')
    c('c t^2:    {:15.8e}'.format(t2))

    check_et1 = abs(t2) < et1
    c('c    |t^2| ({:15.8e})  <  et1 ({:15.8e}): {}'.format(t2, et1, check_et1))
    if check_et1:
        tyc, axc, orc, t2c, r2c, cc = get_cylinder(pl, cmnt)
        if r2c < er1:
            c('c WARNING: r2c ({:15.8e}) is below {:15.8e}'.format(r2c, er1))
        if cc:
            return tyc, axc, orc, t2c, r2c, cmnt
        else:
            return 'o', axc, orc, t2c, r2c, cmnt
    else:
        tyk, axk, ork, t2k, r2k, ck = get_cone(pl, cmnt)
        check_et2 = areclose((0, t2), atol=et2, rtol=None,
                             cmnt=cmnt,
                             name='is t^2 < et2?')
        if check_et2:
            tyc, axc, orc, t2c, r2c, cc = get_cylinder(pl, cmnt)
            can_be_cyl = cc and er2 < r2c
            c('c    er2  ({:15.8e})  <   '
                   'r2c  ({:15.8e}): {}'.format(er2, r2c, can_be_cyl))
            can_be_con = ck and abs(r2k) <= er3
            c('c   |r2k| ({:15.8e})  <=  '
                   'er3  ({:15.8e}): {}'.format(r2k, er3, can_be_con))

            if can_be_cyl and not can_be_con:
                return tyc, axc, orc, t2c, r2c, cmnt
            if can_be_con and not can_be_cyl:
                return tyk, axk, ork, t2k, r2k, cmnt
            if not can_be_cyl and not can_be_con:
                return 'o', axc, orc, t2c, r2c, cmnt
            if can_be_cyl and can_be_con:
                c('c WARNING: both cone and cylinder are possible.')
                return tyc, axc, orc, t2c, r2c, cmnt
        else:
            return tyk, axk, ork, t2k, r2k, cmnt


def adjustABC_cyl(pl, cmnt):
    """
    Adjust A, B or C only if outside the range for cylinder, [0, 1].
    """
    a, b, c = pl
    nm = 'cyl: is {} close to {}'.format
    at = 1e-7
    rt = None
    for v in (0, 1):
        if areclose((v, a), atol=at, rtol=rt):
            a = v
        if areclose((v, b), atol=at, rtol=rt):
            b = v
        if areclose((v, c), atol=at, rtol=rt):
            c = v
    if a == 1:
        ccc = 1.0 / sum((b, c))
        b = b * ccc
        c = c * ccc
    elif b == 1:
        ccc = 1.0 / sum((a, c))
        a = a * ccc
        c = c * ccc
    elif c == 1:
        ccc = 1.0 / sum((a, b))
        a = a * ccc
        b = b * ccc
    else:
        ccc = 2.0 / sum((a, b, c))
        a = a * ccc
        b = b * ccc
        c = c * ccc
    if pl[0] != a or pl[1] != b or pl[2] != c:
        cmnt.append('c Values A, B and C, original | adjusted for cylinder:')
    else:
        cmnt.append('c Values A, B and C: no need to adjust')
    cmnt.append('c A: {:15.8e} | {:15.8e}'.format(pl[0], a))
    cmnt.append('c B: {:15.8e} | {:15.8e}'.format(pl[1], b))
    cmnt.append('c C: {:15.8e} | {:15.8e}'.format(pl[2], c))
    return a, b, c


def get_cylinder(pl_orig, cmnt):
    # Adjust A, B and C so that t21 == 1.0 exactly.
    pl = pl_orig[:]
    a, b, c = adjustABC_cyl(pl[0:3], cmnt)
    pl[0] = a
    pl[1] = b
    pl[2] = c

    t21, xn, yn, zn, cd = get_direction(pl[0:6], cmnt)

    G, H, J, K = pl[6:]
    # Components of Ro are defined from expressions for G, H and J, assuming
    # that (Ro, n) is equal to 0.
    x0 = -G*0.5
    y0 = -H*0.5
    z0 = -J*0.5
    # The cylinder radius is defined from expression for K:
    r2 = x0**2 + y0**2 + z0**2 - K
    cmnt.append("c (0,0,0) projection onto cylinder's axis")
    cmnt.append('c xo:  {:15.8e}'.format(x0))
    cmnt.append('c yo:  {:15.8e}'.format(y0))
    cmnt.append('c zo:  {:15.8e}'.format(z0))
    cmnt.append("c Cylinder's square radius")
    cmnt.append('c r^2: {:15.8e}'.format(r2))
    consistent = r2 >= 0 and cd
    return 'c', (xn, yn, zn), (x0, y0, z0), t21, r2, consistent


def adjustABC_con(pl, cmnt):
    a, b, c = pl
    nm = 'cone: is {} close to {}'.format
    at = 1e-5
    rt = None
    for v in (0, 1):
        if areclose((v, a), atol=at, rtol=rt):
            a = v
        if areclose((v, b), atol=at, rtol=rt):
            b = v
        if areclose((v, c), atol=at, rtol=rt):
            c = v
    if [a, b, c] != pl:
        cmnt.append('c Values A, B and C, original | adjusted for cone:')
        cmnt.append('c A: {:16.9e} | {:16.9e}'.format(pl[0], a))
        cmnt.append('c B: {:16.9e} | {:16.9e}'.format(pl[1], b))
        cmnt.append('c C: {:16.9e} | {:16.9e}'.format(pl[2], c))
    else:
        cmnt.append('c No need to adjust A, B and C for cone')
        cmnt.append('c A: {:16.9e} '.format(pl[0]))
        cmnt.append('c B: {:16.9e} '.format(pl[1]))
        cmnt.append('c C: {:16.9e} '.format(pl[2]))
    return a, b, c


def get_cone(pl_orig, cmnt):
    # Adjust A, B and C so that A <= 1, B <= 1 and C <= 1
    pl = pl_orig[:]
    a, b, c = adjustABC_con(pl[0:3], cmnt)
    pl[0] = a
    pl[1] = b
    pl[2] = c

    t21, xn, yn, zn, cd = get_direction(pl[0:6], cmnt)
    G, H, J, K = pl[6:]
    # For a cone, (R0, n) depends on the position of the cone focus and thus
    # cannot be set to 0. Its value is defined from expressions for G, H and J,
    # and than used again to get x0, y0 and z0.
    ccc = (G*xn + H*yn + J*zn)/(t21 - 1.0)*t21/2.0
    x0 = xn*ccc - G*0.5
    y0 = yn*ccc - H*0.5
    z0 = zn*ccc - J*0.5
    cmnt.append('c Coordinates of the cone focus')
    cmnt.append('c xo:  {:15.8e}'.format(x0))
    cmnt.append('c yo:  {:15.8e}'.format(y0))
    cmnt.append('c zo:  {:15.8e}'.format(z0))
    # r2, expressed from K and others, is used to check consistensy
    r2 = -(G*x0 + H*y0 + J*z0)/2.0 - K
    cmnt.append('c Cone consistensy check (cylinder radius r^2)')
    cmnt.append('c r^2: {:15.8e}'.format(r2))
    return 'k', (xn, yn, zn), (x0, y0, z0), t21, r2, cd


def get_direction(pl, cmnts):
    A, B, C, D, E, F = pl
    t21 = -sum((A, B, C, -3.0))
    # Squares of axis direciton are from A, B and C
    xn2 = (1.0 - A)/t21
    yn2 = (1.0 - B)/t21
    zn2 = (1.0 - C)/t21

    if xn2 < 0.0:
        cmnts.append('c A > 1')
        xn = float('NaN')
    else:
        xn = xn2 ** 0.5
    if yn2 < 0.0:
        cmnts.append('c B > 1')
        yn = float('NaN')
    else:
        yn = yn2 ** 0.5
    if zn2 < 0.0:
        cmnts.append('c C > 1')
        zn = float('NaN')
    else:
        zn = zn2 ** 0.5

    # The choice of axis direction sign: The largest component is positive,
    # the others -- from D, E and F.
    mn2 = max((xn2, yn2, zn2))
    if xn2 == mn2:
        yn = copysign(yn, -D)
        zn = copysign(zn, -F)
    elif yn2 == mn2:
        zn = copysign(zn, -E)
        xn = copysign(xn, -D)
    else:
        xn = copysign(xn, -F)
        yn = copysign(yn, -E)
    cmnts.append('c Components of the axis vector:')
    cmnts.append('c xn: {:15.8e}'.format(xn))
    cmnts.append('c yn: {:15.8e}'.format(yn))
    cmnts.append('c zn: {:15.8e}'.format(zn))

    # Perform consistency checks for cone and cylinder:
    # D^2(C-1) = E^2(A-1) = F^2(B-1)
    e1 = D**2 * (1.0 - C)
    e2 = E**2 * (1.0 - A)
    e3 = F**2 * (1.0 - B)
    e4 = 4.0 * t21**3 * xn2 * yn2 * zn2
    cmnts.append('c Consistensy check D^2(1-C) = E^2(1-A) = F^2(1-B) = '
      '4 (1 + t^2)^3 xn^2 yn^2 zn^2')
    cmnts.append('c D^2 (1 - C):      {:15.8e}'.format(e1))
    cmnts.append('c E^2 (1 - A):      {:15.8e}'.format(e2))
    cmnts.append('c F^2 (1 - B):      {:15.8e}'.format(e3))
    cmnts.append('c 4 (t^2 + 1)^3 xn^2yn^2zn^2: {:15.8e}'.format(e4))
    check = areclose((e1, e2, e3, e4), atol=1e-5, rtol=1e-4,
                     cmnt=cmnts,
                     name='D^2(1-C) = E^2(1-A) = '
                          'F^2(1-B) = 4(1 + t^2)^3 xn^2 yn^2 zn^2')
    consistent = check and float('NaN') not in (xn, yn, zn)
    return t21, xn, yn, zn, consistent


def basis_on_axis(axis):
    """
    Return basis.

    One of the basis vectors has components xn, yn, zn. The others are chosen
    to be as close as possible to the original basis vectors.

    Components of `axis` are normalized to 1, and the component that has the
    maximal absolute value is positive.
    """
    m = max(axis)
    n = 0      # number of shifts
    o = 'xyz'  # axis names
    t = tuple(axis)
    while t[0] != m:
        t = (t[2], t[0], t[1])
        o = o[2] + o[0] + o[1]
        n += 1
    xn, yn, zn = t
    # After i shifts, xn component is the largest one. Now the original basis
    # vectors are named so, that the largest component of the axis is xn, and
    # the 1-st basis vector, i', is `axis`. The second basis vector, j', is most
    # closest to the 2-nd basis vector of the original CS, j. This means, that
    # j' is perpendicular to i' and on the plane built on i' and j.
    i = (xn, yn, zn)
    xn2 = xn**2
    yn2 = yn**2
    zn2 = zn**2
    b = 1.0/((1.0 - yn2)**2 + yn2*(xn2 + zn2))**0.5
    a = -b*yn
    j = (xn*a, yn*a + b, zn*a)
    k = cross_product(i, j)

    # shift vector names back n times
    b = (i, j, k)
    for kkk in range(n):
        i = b[1][1], b[1][2], b[1][0]
        j = b[2][1], b[2][2], b[2][0]
        k = b[0][1], b[0][2], b[0][0]
        b = (i, j, k)
    check_basis(*b)
    # print 'Basis on axis'
    # print axis
    # print b, o
    return b, o[0]


def cross_product(a, b):
    """
    Return cross-product [a, b]
    """
    x = a[1]*b[2] - a[2]*b[1]
    y = b[0]*a[2] - b[2]*a[0]
    z = a[0]*b[1] - a[1]*b[0]
    return x, y, z


def scalar_product(a, b):
    """
    Return scalar product (a, b)
    """
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def check_basis(i, j, k):
    """
    Check that i, j, k are orthogonal, unit and right-hand.
    """
    f = '{:16.8e}'
    vf = f*3
    il = scalar_product(i, i)
    jl = scalar_product(j, j)
    kl = scalar_product(k, k)
    cmnt = []
    if not areclose((il, jl, kl, 1.0), atol=1e-7, rtol=None, cmnt=cmnt):
        for comment in cmnt:
            print(comment)
        print('Basis vectors not normal')
        # raise ValueError('Basis vectors not normal')

    ij = scalar_product(i, j)
    ik = scalar_product(i, k)
    jk = scalar_product(j, k)
    if not areclose((ij, ik, jk, 0.0), atol=1e-7, rtol=None):
        print('i', vf.format(*i))
        print('j', vf.format(*j))
        print('k', vf.format(*k))
        print('products', vf.format(ij, ik, jk))
        print('Basis vectors not orthogonal')
        # raise ValueError('Basis vectors not orthogonal')

    ii = scalar_product(i, cross_product(j, k))
    jj = scalar_product(j, cross_product(k, i))
    kk = scalar_product(k, cross_product(i, j))
    if not areclose((ii, jj, kk, 1.0)):
        print('(i, [j, k])', f.format(ii))
        print('(j, [k, i])', f.format(jj))
        print('(k, [i, j])', f.format(kk))
        print('Basis vectors not right-hand')
        # raise ValueError('Basis vectors not right-hand')
    return i, j, k


def transform(p, b, o):
    """
    Return coordinates of point `p` in the basis `b`, which center has
    coordinates `o`.

    Vectors of basis `b` must be orthonormal.
    """
    x, y, z = p
    i, j, k = b
    X, Y, Z = o
    dv = (x-X, y-Y, z-Z)
    xp = scalar_product(dv, i)
    yp = scalar_product(dv, j)
    zp = scalar_product(dv, k)
    return xp, yp, zp


if __name__ == '__main__':
    a = 1.0
    b = a + 1e-7
    c = a - 1e-7
    l = (a, b, c, 0)
    print l
    print areclose(l, atol=1e-6)
