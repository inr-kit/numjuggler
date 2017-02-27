"""
Functions to convert an arbitrary GQ cylinder into C/X+TR-defined cylinder.
"""

from __future__ import print_function

try:
    # try because numpy might be unavailable.
    import numpy
except ImportError:
    print("Numpy package is required for --mode nogq but cannot ")
    print("be found. Install it with ")
    print("")
    print(" > pip install numpy")
    print("")
    raise
except:
    raise


def get_k(p):
    # define a2, c and vector k
    ABC = p[0:3]
    DEF = p[3:6]/2.

    # define a2. Its definition deends on whether all DEF are zero or not.
    if (DEF == 0.).all():
        # all DEF are zero. This means that only one of components of k is
        # non-zero.
        a2 = ABC.max()
    else:
        # at least one of DEF is non-zero.
        ii = abs(DEF).argmax()
        iv = DEF[ii]
        a2 = numpy.roll(ABC, 1)[ii] - DEF[DEF != iv].prod()/iv

    # expression for gamma holds for any ABC and DEF:
    g = ABC.sum() - 3.0*a2

    # vector parallel to the cylinder/cone axis:
    A, B, C = ABC
    D, E, F = DEF
    k = numpy.array((A - a2 + D + F,
                     D + B - a2 + E,
                     F + E + C - a2))
    k = k / (k**2).sum()**0.5

    return a2, g, k


def cylinder(p, a2, g, k):
    # a2, g and k -- as returned from get_k

    A, B, C, D, E, F, G, H, J, K = p

    # vector i of the 'simple' CS
    i = p[6:9]  # G, H, J
    GHJ2 = (i**2).sum()
    i = i / GHJ2**0.5  # normalize

    # radius
    r2 = GHJ2 / 4. / a2 - K

    # x coordinate of CS in the simple CS:
    x0 = GHJ2**0.5 / 2. / a2

    # vector j
    j = numpy.cross(k, i)
    return r2**0.5, -x0, i, j


def get_a2(p):
    # aliases
    A, B, C, D, E, F, G, H, J, K = p
    ABC = A + B + C
    a2dic = {}
    if D != 0.:
        a2 = C - E*F/D*0.5
        c = ABC - 2*a2
    if E != 0.:
        a2dic['E'] = A - D*F/E*0.5
    if F != 0.:
        a2dic['F'] = B - D*E/F*0.5
    if D == E == F == 0.:
        #
        pass
    for k, a2 in list(a2dic.items()):
        c = ABC - 2.0*a2
    return a2, c


def is_gq_cylinder(p):
    """
    Check that the GQ parameters in p describe a cylinder.

    And return normalized set.
    """
    a, b, c, d, e, f, g, h, j, k = p

    # A, B and C are non-negative
    if a < 0 or b < 0 or c < 0:
        print(' not a cylinder since a, b or c is negative: ',  p[0:3])
        raise ValueError()

    if not numpy.isclose(d*e*f, -8.*(1.-a)*(1.-b)*(1.-c)):
        print(' D*E*F differs from -8(1-A)(1-B)(1-C)', p)
        raise ValueError()

    return 1.0/p[0:3].sum() * p


def gq_axis(p):
    """
    return coordinates of the cylinder axis,  and the normalized p
    """
    # aliases
    a, b, c, d, e, f, g, h, j, k = p

    # direct formula, x = (1 - a)**0.5 can be unprecise when a close to 1. Thus,
    # we use it only for the lowest from a, b or c
    if c > a < b:
        # a is the minimal coeff
        xc = (1. - a)**0.5
        yc = -d/xc*0.5
        zc = -f/xc*0.5
    elif a > b < c:
        # b is the minimal coeff
        yc = (1. - b)**0.5
        xc = -d/yc*0.5
        zc = -e/yc*0.5
    else:
        # c is the minimal
        zc = (1. - c)**0.5
        xc = -f/zc*0.5
        yc = -e/zc*0.5
    return numpy.array((xc, yc, zc))


def skprime(c):
    """
    c -- only one vector. Add two other that are orthonormal.
    """
    x, y, z = c
    j = numpy.array((0., 1., 0.))
    k = numpy.array((0., 0., 1.))
    if x == 1.:
        # axis coincides with x-axis.
        pass
    elif y == 1.:
        # c coincides with y-axis. Use z to define j'
        j = numpy.cross(k, c)
        j = j / numpy.dot(j, j)**0.5
        k = numpy.cross(c, j)
    else:
        # c coincides with z axis. Use j to define new k'
        k = numpy.cross(c, j)
        k = k / numpy.dot(k, k)**0.5
        j = numpy.cross(k, c)
    return c, j, k


def gq_orig(p, c):
    """
    rerurn coordinates of a point that axis c goes through.

    Axis c is needed to choose the closest point to the coordinate origin.

    """
    # aliases
    a, b, C, d, e, f, g, h, j, k = p
    xc, yc, zc = c
    M = numpy.array([[2.*a + xc, d + yc, f + zc],
                     [        d,   2.*b,      e],
                     [        f,      e,  2.*C]])
    B = numpy.array((-g, -h, -j))

    o = numpy.linalg.solve(M, B)
    return o


def gq_radius(p, o):
    """
    return cylinder's radius, where p - GQ parameters, o -- point on the axis.
    """
    # aliases
    a, b, c, d, e, f, g, h, j, k = p
    xo, yo, zo = o
    rrr = numpy.array((-k, xo**2.*a, yo**2.*b, zo**2.*c,
                       xo*yo*d, xo*zo*f, yo*zo*e))
    r2 = rrr.sum()
    if r2 < 0:
        print('Radius is imaginary: r^2=', r2)
    return r2**0.5


def plane(v, p1, p2):
    """
    Return parameters of p card for the plane defined
    by vector v and two points p1 and p2.
    """
    v1 = v
    # second vector:
    v2 = p2 - p1

    # vector perpendicular to the plane. Its components are actualy the coeffs
    # A, B and C.
    abc = numpy.cross(v1, v2)
    A, B, C = abc
    D = - numpy.dot(p1, abc)
    return A, B, C, D


def gq_cylinder(gq):
    """
    Computes parameters of a cylinder defined by the GQ card. Returns tuple (c,
    p, r), where

        c -- vector parallel to the cylinder axis,
        p -- coordinate of the point of the cylinder axis, closest to the
             origin, and
        r -- cylinder radius.

    """

    # Normalized set of GQ parameters, axis c, point p and radius r
    n = is_gq_cylinder(gq)
    c = gq_axis(n)
    p = gq_orig(n, c)
    r = gq_radius(n, p)

    # Rotational matrix of the coordinate system with x // to the cylinder axis,
    # and coordinates of the point p in this SC:
    M = numpy.vstack(skprime(c))  # rotational matrix
    pp = numpy.dot(M, p)          # position of p in the new CS

    res = {}
    # c/x parameters
    res['s c/x'] = (pp[1], pp[2], r)
    res['t c/x'] = (0, 0, 0) + tuple(c) + tuple(M[1, :]) + tuple(M[2, :])

    # cx parameters
    res['s cx'] = (r, )
    res['t cx'] = tuple(p) + tuple(c)

    return res


def get_gq_params(l):
    """
    Returns a numpy array of GQ card parameters. The string l represents (a part
    of) the GQ card.
    """
    p, pl = l.lower().split('gq')
    return numpy.array(list(map(float, pl.split())))


if __name__ == '__main__':
    # trial sets, from ivvs model:
    pd = {}
    pd[517] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731       8.9081601     112.2141090 444.8005144   52053.7148001 '
    pd[518] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731       8.9081601     112.2141090 444.8005144   51953.7148001 '

    pd[520] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731      17.0608040     115.1814287 527.3458317   72336.8646999 '
    pd[521] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731      17.0608040     115.1814287 527.3458317   72236.8646999 '

    pd[513] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731      -4.7726457     149.8018138 444.8005144   54401.7148002 '
    pd[528] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731      -4.7726457     149.8018138 444.8005144   54501.7148002 '

    pd[529] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731       3.3799982     152.7691336 527.3458317   74784.8647000 '
    pd[530] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731       3.3799982     152.7691336 527.3458317   74684.8647000 '
    pd[532] = '      GQ        0.1266259       0.8843003       0.9890738      -0.6357644 0.0711100       0.1953731       6.8598356     132.6895083 493.1163947   64843.3354134 '

    # GQ from m1_ model in to5
    pd[25177] = '       GQ        0.6951738       0.9781145       0.3267118       0.1633559 -0.2427779       0.9060594   -1292.6456577     346.3633601 -932.2182196  664976.9633871 '
    pd[25185] = '       GQ        0.6951738       0.9781145       0.3267118       0.1633559 -0.2427779       0.9060594   -1282.2945347     343.5897850 -924.7532926  654369.6343547 '
    pd[25183] = '       GQ        0.6951738       0.9781145       0.3267118       0.1633559 -0.2427779       0.9060594   -1276.1553470     366.5015456 -924.7532926  654510.2939547 '
    pd[25187] = '       GQ        0.6951738       0.9781145       0.3267118       0.1633559 -0.2427779       0.9060594   -1279.3802323     354.4661098 -924.7532926  654401.3312546 '
    pd[25179] = '       GQ        0.6951738       0.9781145       0.3267118       0.1633559 -0.2427779       0.9060594   -1289.7313552     357.2396849 -932.2182196  665008.6602870 '
    pd[25181] = '       GQ        0.6951738       0.9781145       0.3267118       0.1633559 -0.2427779       0.9060594   -1285.5553713     369.0202746 -931.5323151  664136.1672603 '
    pd[25099] = '       GQ        0.3874553       0.9391049       0.6734399       0.3862692 0.2820349      -0.8945003    -251.4879218      79.2938372 378.6739698   53230.4757183 '
    pd[25100] = '       GQ        0.3874553       0.9391049       0.6734399       0.3862692 0.2820349      -0.8945003    -210.0745168      66.2362407 316.3163888   37142.2100034 '

    po = None
    for xo0 in [1e-4, 791.866]:

        print('xo0', xo0, '***'*20)

        for n in [532, 25099, 25100, 25177, 25185, 25183, 25187, 25179, 25181]:
            p = get_gq_params(pd[n])
            p = is_gq_cylinder(p)
            # # axis coordinates and normalized p
            # c = gq_axis(p)
            # o = gq_orig(p, c) #, o0=(xo0, 1, 1))
            # r = gq_radius(p, o)
            # x, y, z = o
            # trrot = '   {} {} {}'.format(*c) # rotational part of TR card
            # print '{0} {0} cx {1}'.format(n, r)
            # print 'tr{} {} {} {}'.format(n, x, y, z), trrot

            # # c/x card. Here one needs to define all coordinate vectors in the new CS,
            # # and get y0 and z0 -- position of cylinder axis in the new CS.
            # i, j, k = skprime(c)
            # M = numpy.vstack((i, j, k))
            # op = numpy.dot(M, o)
            # u, v, w = op
            # print 'c'
            # print '{} {} c/x {} {} {}'.format(n, n, v, w, r)
            # print 'tr{} 0 0 0 '.format(n), trrot, '{} {} {}'.format(*j), '{} {} {}'.format(*k)
            # print '-'*20

            r = gq_cylinder(p)
            print(r)





