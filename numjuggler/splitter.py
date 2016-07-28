"""
Analog for str.split() that splits an arbitrary cell card.

Cell card consists of material specifications, geometry, and list of keywords.
The part with material specifications can only contain integers and floats.

The geometry description part can contain integers, points (for macro body
facets), parentheses, the colon, minus (and plus, formally), and hash.

The keyword part can contain floats, alpha-numeric keywords, equal signs and
parentheses.

Everywhere the repitition syntax is possible, that is Ni, Nr, etc.  
"""

# List of cell parameter keywords
LoCL = ['imp',
        'vol',
        'pwt',
        'ext',
        'fcl',
        'wwn',
        'dxc',
        'nonu',
        'pd',
        'tmp',
        'u',
        '*fill',
        'fill',
        'lat']

# List of shorthand features
LoSH = ['r',
        'ilog',
        'i',
        'm',
        'j']

def split_by_state(inpt):
    tl = inpt.split() # list of tokens
    vl = []           # list of (v, t) -- value and its type

    # Read cell name and material specs
    c = tl.pop(0)
    m = tl.pop(0)
    vl += [(c, 'cell'), (m, 'mat')]
    if int(m) > 0:
        d = tl.pop(0)
        vl += [(d, 'rho')]

    state = 'geom'
    while tl:
        n = tl[0]
        if state == 'geom':
            # check if param starts:
            for kw in LoCL:
                if kw in n:
                    state = 'param'
                    break

        elif state == 'param':


def _cut(s, subs):
    """
    Cut subs from the begining of s.
    """
    return s[s.find(subs) + len(subs): ]


def split_head(inpt):
    """
    Return [Cellname, material, density] and the rest of the inpt.

    The argument ``inpt`` is a string representing the meaningful parts of a cell card that does not 
    use the ``LIKE n BUT`` syntax.

    """

    t = inpt.split()
    c = t.pop(0)
    m = t.pop(0)
    res = (c, m)
    if int(m) > 0:
        d = t.pop(0)
        res += (d, )

    # remove c, m and d from inpt:
    for e in res:
        inpt = _cut(inpt, e)

    return res, inpt


def split_geometry(inpt):
    """
    Return list of tokens of geometry definition, and the rest of inpt.

    The cell name and material specs should be already removed with split_head().
    """

    # geometry description goes until the first keyword, that must be alpha-numeric.
    # Find where geometry ends, taking into account repetition characters i and r:
    for i in range(1, len(inpt)):
        if inpt[i].isalpha() and not inpt[i-1].isdigit():
            break
    geom = inpt[:i]
    rest = inpt[i:]

    # add spaces around parentheses, colons, and #-s.
    for c in '()#:':
        geom = geom.replace(c, ' ' + c + ' ')



if __name__ == '__main__':
    s = {}
    s[0] = '1 0 1 -5'
    s[1] = '2 5 -10.3 (3:4)'
    s[2] = '2 5 -10.3 \n (3:4)'

    for l in s.values():
        print repr(l)
        print split_head(l)
        print '--'*30
