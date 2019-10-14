from __future__ import print_function, division, nested_scopes
import six
try:
    import pirs.core.trageom.vector as vector
except:
    vector = None

if six.PY2 and vector is not None:
    from math import copysign, isnan


    def areclose(l, rtol=1e-4, atol=1e-7, cmnt=None, name='', detailed=True):
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
            c('Are close check: ' + name + ': {}'.format(result))
            if detailed:
                c('  values: ' + ' '.join('{:15.8e}'.format(v) for v in l))
                c('  B:      {:15.8e}'.format(B))
                c('  A:      {:15.8e}'.format(A))
                c('  B - A:  {:15.8e}'.format(B - A))
                c('  atol:   ' + astr)
                c('  rtol*b: ' + rstr)
        return result


    def get_params(card):
        """
        Return parameters of the GQ card.
        """
        p1, p2 = card.lower().split('gq')
        # Check if there is transformation:
        tr = len(p1.split()) > 1
        return tr, map(float, p2.split())


    def get_cone_or_cyl(pl):
        """
        See notes from 14.03.2018
        """
        cmnt = []

        # Define normalization coeff gamma:
        A, B, C, D, E, F, G, H, J, K = pl
        ABC = sum((A, B, C))
        cmnt.append(' A, B, C:' + ' '.join('{:15.8e}'.format(v) for v in (A, B, C)))
        cmnt.append(' D, E, F:' + ' '.join('{:15.8e}'.format(v) for v in (D, E, F)))
        cmnt.append(' G, H, J:' + ' '.join('{:15.8e}'.format(v) for v in (G, H, J)))
        cmnt.append('       K:' + ' {:15.8e}'.format(K))

        # List of normalization coefficients. 1 is always assumed
        gammas = [1.0, -1.0]
        tDEF = 5e-5
        tABC = 1e-9
        if areclose((0, E), atol=tDEF, rtol=None):
            if areclose((1, B), atol=tABC, rtol=None):
                g = 1.0/B
                gammas.append(g)
                cmnt.append('gamma_B = {:15.8e}'.format(g))
            if areclose((1, C), atol=tABC, rtol=None):
                g = 1.0/C
                gammas.append(g)
                cmnt.append('gamma_C = {:15.8e}'.format(g))
        else:
            g = 2*E/(2*E*A - D*F)
            gammas.append(g)
            cmnt.append('gamma_E = {:15.8e}'.format(g))

        if areclose((0, F), atol=tDEF, rtol=None):
            if areclose((1, A), atol=tABC, rtol=None):
                g = 1.0/A
                gammas.append(g)
                cmnt.append('gamma_A = {:15.8e}'.format(g))
            if areclose((1, C), atol=tABC, rtol=None):
                g = 1.0/C
                gammas.append(g)
                cmnt.append('gamma_C = {:15.8e}'.format(g))
        else:
            g = 2*F/(2*F*B - D*E)
            gammas.append(g)
            cmnt.append('gamma_F = {:15.8e}'.format(g))

        if areclose((0, D), atol=tDEF, rtol=None):
            if areclose((1, B), atol=tABC, rtol=None):
                g = 1.0/B
                gammas.append(g)
                cmnt.append('gamma_B = {:15.8e}'.format(g))
            if areclose((1, A), atol=tABC, rtol=None):
                g = 1.0/A
                gammas.append(g)
                cmnt.append('gamma_A = {:15.8e}'.format(g))
        else:
            g = 2*D/(2*D*C - E*F)
            gammas.append(g)
            cmnt.append('gamma_d = {:15.8e}'.format(g))

        # Ensure that gamma=1 is considered first
        gammas = set(gammas)
        gammas.remove(1)
        gammas.remove(-1)
        gammas = (1.0, -1.0) + tuple(gammas)
        for gamma in gammas:
            t2, n, R0c, r2c, R0k, r2k, c1, c2 = get_surface_parameters(gamma, pl)
            n2 = scalar_product(n, n)
            R0kn = scalar_product(n, R0k)
            R0k2 = scalar_product(R0k, R0k)
            R0cn = scalar_product(n, R0c)
            R0c2 = scalar_product(R0c, R0c)
            tt = t2**0.5 if t2 >= 0 else float('nan')
            rc = r2c**0.5 if r2c >= 0 else float('nan')
            rk = r2k**0.5 if r2k >= 0 else float('nan')
            cmnt.append('gamma: 1 + {:15.8e}'.format(gamma - 1.0))
            cmnt.append('     t^2: {:15.8e}'.format(t2))
            cmnt.append('      t : {:15.8e}'.format(tt))
            cmnt.append('      n : ' + ' '.join('{:15.8e}'.format(v) for v in n))
            cmnt.append('   (n,n): {:15.8e}'.format(n2))
            cmnt.append('     r^2: {:15.8e}  {:15.8e}'.format(r2c, r2k))
            cmnt.append('       r: {:15.8e}  {:15.8e}'.format(rc, rk))
            cmnt.append('     R0c: ' + ' '.join('{:15.8e}'.format(v) for v in R0c))
            cmnt.append('     R0k: ' + ' '.join('{:15.8e}'.format(v) for v in R0k))
            cmnt.append('  (n,R0): {:15.8e}  {:15.8e}'.format(R0cn, R0kn))
            cmnt.append(' (R0,R0): {:15.8e}  {:15.8e}'.format(R0c2, R0k2))
            cmnt.append('      c1: {:15.8e}'.format(c1))
            cmnt.append('      c2: {:15.8e}'.format(c2))

            # Check parameters common for cone and cylinder
            if isnan(n2) or areclose((0, n2), atol=1e-4, rtol=None):
                cmnt.append('        gamma sorted out due to n')
                continue

            # Evaluate surface at some points
            distances = (-100, -10, -1, 0, 1, 10, 100)
            rsdc = {}  # residuals for cylinder
            rsdk = {}  # residuals for cone
            ni, nj, nk = vector.Vector3(car=n).basis()
            if areclose((0, r2c), atol=1e-6, rtol=None) or isnan(rc) or isnan(R0c2):
                can_be_cylinder = False
                cmnt.append('        cannot be cylinder due to r2 or R0')
            else:
                can_be_cylinder = True
                r0 = vector.Vector3(car=R0c)
                nj.R = rc
                nk.R = rc
                for d in distances:
                    r00 = r0 + d*ni
                    d1 = evaluate_gq(pl, (r00 + nj).car)
                    d2 = evaluate_gq(pl, (r00 - nj).car)
                    d3 = evaluate_gq(pl, (r00 + nk).car)
                    d4 = evaluate_gq(pl, (r00 - nk).car)
                    rsdc[d] = (d1, d2, d3, d4)
            if areclose((0, t2), atol=1e-6, rtol=None) or isnan(tt) or isnan(R0k2):
                can_be_cone = False
                cmnt.append('        cannot be cone due to t2 or R0')
            else:
                can_be_cone = True
                r0 = vector.Vector3(car=R0k)
                for d in distances:
                    rkd = tt * d
                    nj.R = rkd
                    nk.R = rkd
                    r00 = r0 + d*ni
                    d1 = evaluate_gq(pl, (r00 + nj).car)
                    d2 = evaluate_gq(pl, (r00 - nj).car)
                    d3 = evaluate_gq(pl, (r00 + nk).car)
                    d4 = evaluate_gq(pl, (r00 - nk).car)
                    rsdk[d] = (d1, d2, d3, d4)

            # Compare residuals for cone and cylinder and choose one
            if can_be_cone and can_be_cylinder:
                typ = 0
                for d in distances:
                    dc = scalar_product(rsdc[d], rsdc[d])
                    dk = scalar_product(rsdk[d], rsdk[d])
                    if dc <= dk:
                        typ += 1
                    else:
                        typ -= 1
                if typ > 0:
                    typ = 'c'
                else:
                    typ = 'k'
            elif can_be_cone:
                typ = 'k'
            elif can_be_cylinder:
                typ = 'c'
            else:
                typ = 'o'
                continue

            # Prepare output
            if typ == 'k':
                org = R0k
                r2 = r2k
                rsd = rsdk
            elif typ == 'c':
                org = R0c
                r2 = r2c
                rsd = rsdc

            rsdmax = max(map(abs, sum(rsd.values(), ())))
            cmnt.append(' Residuals for {}, {:15.8e}'.format(typ, rsdmax))
            for d in distances:
                cmnt.append(' at d={:10.3e}:'.format(d) + ' '.join('{:15.8e}'.format(v) for v in rsd[d]))
            if rsdmax > 1e-1:
                typ = 'o'
                continue
            else:
                cmnt.append(' Final max. residual for {}, {:15.8e}'.format(typ, rsdmax))

            cmnt = ['c ' + c for c in cmnt]
            return typ, n, org, t2, r2, cmnt
        typ = 'o'
        cmnt = ['c ' + c for c in cmnt]
        return typ, None, None, None, None, cmnt


    def get_surface_parameters(gamma, pl):
        """
        pl -- list of original GQ parameters,
        gamma -- normlaization coefficient
        """
        # normliaze GQ parameters
        pl = (gamma*v for v in pl)
        A, B, C, D, E, F, G, H, J, K = pl

        # parameter t^2
        t2 = sum((2.0, -A, -B, -C))

        # parameters xn, yn, zn
        t21 = sum((3.0, -A, -B, -C))
        xn2 = (1 - A)/t21
        yn2 = (1 - B)/t21
        zn2 = (1 - C)/t21
        xn = float('nan')
        yn = float('nan')
        zn = float('nan')
        if xn2 >= 0:
            xn = xn2 ** 0.5
        if yn2 >= 0:
            yn = yn2 ** 0.5
        if zn2 >= 0:
            zn = zn2 ** 0.5
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

        # Parameters x0, y0, z0
        # and r2 (cylinder radius, or error in cone focus position)

        # Assuming that t2 is 0 (i.e. formulae for cylinder)
        x0c = -G * 0.5
        y0c = -H * 0.5
        z0c = -J * 0.5
        r2c = x0c**2 + y0c**2 + z0c**2 - K

        # Formulae for cone
        cR0n = (G*xn + H*yn + J*zn)*t21/2.0
        if t2 > 0:
            cR0n = cR0n / t2
        else:
            cR0n = copysign(float('inf'), cR0n*t2)
        x0k = xn*cR0n - G*0.5
        y0k = yn*cR0n - H*0.5
        z0k = zn*cR0n - J*0.5
        r2k = -(G*x0k + H*y0k + J*z0k)/2 - K

        # Consistency checks
        rgh1 = D*E*F
        lft1 = -8*(1 - A)*(1 - B)*(1 - C)
        rgh2 = (G*xn + H*yn + J*zn)**2 * t21
        lft2 = G**2*(1 - A) + H**2*(1 - B) + J**2*(1 - C) - G*H*D - J*G*F - J*H*E
        c1 = rgh1 - lft1
        c2 = rgh2 - lft2
        return (t2, (xn, yn, zn),
                (x0c, y0c, z0c), r2c,    # cylinder formulae
                (x0k, y0k, z0k), r2k,    # cone formulae
                c1, c2)


    def evaluate_gq(pl, p):
        """
        Evaluate GQ equation at point p.
        """
        x, y, z = p
        A, B, C, D, E, F, G, H, J, K = pl
        d = (A*x**2 + B*y**2 + C*z**2 +
             D*x*y  + E*y*z  + F*z*x  +
             G*x    + H*y    + J*z    + K)
        return d


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
        if not areclose((il, jl, kl, 1.0), atol=1e-7, rtol=None, cmnt=cmnt, name='Basis vector normalization'):
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
        print(l)
        print(areclose(l, atol=1e-6))
