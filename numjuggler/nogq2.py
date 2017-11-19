from math import copysign


def areclose(l, rtol=1e-4, atol=1e-7, cmnt=None):
    """
    Check if all elements in the list l are close to each other.

    Implementation based on numpy.isclose formula
    """
    if rtol == None:
        rtol = 3.0
    A = min(l)
    B = max(l)
    b = max(map(abs, l))
    if cmnt is not None:
        # assume it is a list of comments. Add here information
        c = cmnt.append
        c('c     Are close check:')
        c('c     B - A <= atol and <= rtol*b')
        c('c     B - A:  {:15.8e}'.format(B - A))
        c('c     atol:   {:15.8e}'.format(atol))
        c('c     rtol*b: {:15.8e}'.format(rtol*b))
    return B - A <= atol and B - A <= rtol*b


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

    Coefficients D, E and F also depend on the cone angle and xn, yn, zn. These
    equations are used to check if the set A -- K describes a cone/cylinder.
    """
    A, B, C = pl[0:3]

    # For a cone, t21 = 1 + t^2, where t is the tan of half-angle. For a
    # cylinder, t21 is equal or slightly above 1.
    t21 = -sum((A, B, C, -3.0))

    cmnt = []
    c = cmnt.append
    c('c GQ parameters: ')
    c('c t^2 + 1: {:15.8e}'.format(t21))

    ccc = []
    if areclose((1.0, t21), atol=2e-7, rtol=None, cmnt=ccc):
        typ, axis, orig, t21, r2, cmn2 = get_cylinder(pl)
        return typ, axis, orig, t21, r2, cmnt + cmn2
    elif t21 < 1.0:
        cmnt.extend(ccc)
        c('c Square tan is negative, t^2 = {:15.8e}'.format(t21 - 1.0))
        return 'o', None, None, None, None, cmnt
    else:
        typ, axis, orig, t21, r2, cmn2 = get_cone(pl)
        return typ, axis, orig, t21, r2, cmnt + cmn2


def get_cylinder(pl):
    t21, xn, yn, zn, cmnt = get_direction(pl[0:6])
    if None in (xn, yn, zn):
        return 'o', None, None, None, None, cmnt
    c = cmnt.append

    G, H, J, K = pl[6:]
    # Components of Ro are defined from expressions for G, H and J, assuming
    # that (Ro, n) is equal.
    x0 = -G*0.5
    y0 = -H*0.5
    z0 = -J*0.5
    # The cylinder radius is defined from expression for K:
    r2 = x0**2 + y0**2 + z0**2 - K
    c('c Coordinates of the cylinder center, and square radius')
    c('c xo:  {:15.8e}'.format(x0))
    c('c yo:  {:15.8e}'.format(y0))
    c('c zo:  {:15.8e}'.format(z0))
    c('c r^2: {:15.8e}'.format(r2))
    if r2 < 0.0:
        c('c Negative square of cylinder radius')
        return 'o', None, None, None, None, cmnt
    if areclose((0.0, r2), rtol=None):
        c('c WARNING: r^2 is close to zero')
    return  'c', (xn, yn, zn), (x0, y0, z0), t21, r2, cmnt


def get_cone(pl):
    t21, xn, yn, zn, cmnt = get_direction(pl[0:6])
    if None in (xn, yn, zn):
        return 'o', None, None, None, None, cmnt
    c = cmnt.append
    G, H, J, K = pl[6:]
    # For a cone, (R0, n) depends on the position of the cone focus and thus
    # cannot be set to 0. Its value is defined from expressions for G, H and J,
    # and than used again to get x0, y0 and z0.
    ccc = (G*xn + H*yn + J*zn)/(t21 - 1.0)*t21
    x0 = xn*ccc - G*0.5
    y0 = yn*ccc - H*0.5
    z0 = zn*ccc - J*0.5
    c('c Coordinates of the cone focus')
    c('c xo:  {:15.8e}'.format(x0))
    c('c yo:  {:15.8e}'.format(y0))
    c('c zo:  {:15.8e}'.format(z0))
    # Expresison for K is used to check consistensy
    e1 = G*x0 + H*y0 + J*z0
    e2 = -K*2.0
    c('c Cone consistensy check -2K = Gx0 + H*y0 + J*z0')
    c('c -2K:               {:15.8e}'.format(e2))
    c('c Gx0 + H*y0 + J*z0: {:15.8e}'.format(e1))
    if not areclose((e1, e2), cmnt=cmnt):
        c('c Consistensy check failed')
        return 'o', None, None, None, None, cmnt
    return 'k', (xn, yn, zn), (x0, y0, z0), t21, 0.0, cmnt


def get_direction(pl):
    A, B, C, D, E, F = pl
    t21 = -sum((A, B, C, -3.0))
    # Squares of axis direciton are from A, B and C
    xn2 = (1.0 - A)/t21
    yn2 = (1.0 - B)/t21
    zn2 = (1.0 - C)/t21

    cmnts = []
    if xn2 < 0.0:
        cmnts.append('c A < 1')
        xn = None
    else:
        xn = xn2 ** 0.5
    if yn2 < 0.0:
        cmnts.append('c B < 1')
        yn = None
    else:
        yn = yn2 ** 0.5
    if zn2 < 0.0:
        cmnts.append('c C < 1')
        zn = None
    else:
        zn = zn2 ** 0.5
    if cmnts:
        return t21, xn, yn, zn, cmnts

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

    # Perform consistency checks for cone and cylinder:
    # D^2(C-1) = E^2(A-1) = F^2(B-1)
    e1 = D**2 * (1.0 - C)
    e2 = E**2 * (1.0 - A)
    e3 = F**2 * (1.0 - B)
    e4 = 4.0 * t21**3 * xn**2 * yn**2 * zn**2
    cmnts = []
    c = cmnts.append
    c('c Components of the axis vector:')
    c('c xn: {:15.8e}'.format(xn))
    c('c yn: {:15.8e}'.format(yn))
    c('c zn: {:15.8e}'.format(zn))
    c('c Consistensy check D^2(1-C) = E^2(1-A) = F^2(1-B) = '
      '4 (1 + t^2)^3 xn^2 yn^2 zn^2')
    c('c D^2 (1 - C):      {:15.8e}'.format(e1))
    c('c E^2 (1 - A):      {:15.8e}'.format(e2))
    c('c F^2 (1 - B):      {:15.8e}'.format(e3))
    c('c 4 t21^3 xnynzn^2: {:15.8e}'.format(e4))
    if not areclose((e1, e2, e3, e4), rtol=None, cmnt=cmnts):
        c('c Consistensy check fails')
        return t21, None, None, None, cmnts
    return t21, xn, yn, zn, cmnts


def basis_on_axis(axis):
    """
    Return basis.

    One of the basis vectors has components xn, yn, zn. The others are chosen
    to be as close as possible to the original basis vectors.

    Components of `axis` are normalized to 1, and the components that has the
    maximal absolute value is positive.
    """
    m = max(axis)
    n = 0     # number of shifts
    o = 'xyz' # axis names
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
    if not areclose((il, jl, kl, 1.0)):
        raise ValueError('Basis vectors not normal')

    ij = scalar_product(i, j)
    ik = scalar_product(i, k)
    jk = scalar_product(j, k)
    if not areclose((ij, ik, jk, 0.0), rtol=None):
        print 'i', vf.format(*i)
        print 'j', vf.format(*j)
        print 'k', vf.format(*k)
        print 'products', vf.format(ij, ik, jk)
        raise ValueError('Basis vectors not orthogonal')

    ii = scalar_product(i, cross_product(j, k))
    jj = scalar_product(j, cross_product(k, i))
    kk = scalar_product(k, cross_product(i, j))
    if not areclose((ii, jj, kk, 1.0)):
        print '(i, [j, k])', vf.format(ii)
        print '(j, [k, i])', vf.format(jj)
        print '(k, [i, j])', vf.format(kk)
        raise ValueError('Basis vectors not right-hand')
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
