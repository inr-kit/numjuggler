"""
Functions for parsing MCNP input files.
"""
import re
import warnings


# regular expressions
re_int = re.compile('\D{0,1}\d+') # integer with one prefix character
re_ind = re.compile('\[.+\]')     # interior of square brackets for tally in lattices
re_rpt = re.compile('\d+[rRiI]')  # repitition syntax of MCNP input file
re_prm = re.compile('((imp:n|imp:p|tmp)\s+\S+)')     # imp or tmp parameters in cell card
re_prm = re.compile('[it]mp:*[npe]*[=\s]+\S+')

fmt_d = lambda s: '{{:<{}d}}'.format(len(s))
fmt_g = lambda s: '{{:<{}g}}'.format(len(s))
fmt_s = lambda s: '{{:<{}s}}'.fromat(len(s))
fmt_s = lambda s: '{}'


class __CIDClass(object):
    """
    There are two levels of card types. 1-st level is purely defined by card
    position in the input file.  There can be:
          * message card
          * title card
          * cell card
          * surface card
          * data card.

    Data cards can be of different type that is defined by the card's first
    entry. Therefore data cards can be characterized by type of the 2-nd level:
          * m cards,
          * f cards,
          * etc.

    This class is to describe the 1-st level of card types.
    """
    # no-information cards
    comment = -1
    blankline = -2
    # card types in order they appear in MCNP input
    message = 1
    title = 2
    cell = 3
    surface = 4
    data = 5

    @classmethod
    def get_name(cls, cid):
        """
        Return the name of the card type by its index.
        """
        for k, v in cls.__dict__.items():
            if '__' not in k and v == cid:
                return k
        else:
            raise ValueError()

CID = __CIDClass()

class Card(object):
    """
    Representation of a card.
    """
    def __init__(self, lines, ctype, pos, debug=None):

        # Original lines, as read from the input file
        self.lines = lines

        # card type by its position in the input. See CID class.
        self.ctype = ctype

        # data card type. Defined from the get_values() method.
        # has sence only to data cards (see ctype). For other card types
        # is None.
        self.dtype = None

        # Input file line number, where the card was found.
        self.pos = pos

        # File-like object to write debug info (if not None)
        self.debug = debug

        # template string. Represents the general structure of the card. It is
        # a copy of lines, but meaningful parts are replaced by format
        # specifiers, {}
        self.template = ''

        # List of strings represenging meaningful parts of the card. The
        # original multi-line string card is obtained as
        # template.format(*input)
        self.input = []

        # Dictionary of parts that are removed from input before processing it.
        # For example, repitition syntax (e.g. 5r or 7i) is replaced with '!'
        # to prevent its modification.
        self.hidden = {}

        # List of (v, t) tuples, where v -- value and t -- its type.
        self.values = []

        # Split card to template and meaningful part is always needed. Other operations
        # are optional.
        self.get_input()

    def print_debug(self, comment, key='tihv'):
        d = self.debug
        if d:
            print >> d, 'Line {}, {} card. {}'.format(self.pos, CID.get_name(self.ctype), comment)
            if 't' in key:
                print >> d, '    template:', repr(self.template)
            if 'i' in key:
                print >> d, '    input:   ', self.input
            if 'h' in key:
                print >> d, '    hidden:  ', self.hidden
            if 'v' in key:
                print >> d, '    values:  ', self.values

    def get_input(self):
        """
        Recompute template, input and hidden attributes from lines
        """

        mline = ''.join(self.lines)
        bad_chars = '\t'
        for c in bad_chars:
            if c in mline:
                if self.debug:
                    self.print_debug('get_input: bad character in input cards', '')
                else:
                    raise ValueError('Bad character in input file. Run with --debug option.')

        if self.ctype in (CID.comment, CID.blankline):
            # nothing to do for comments or blanklines:
            self.input = ''
            self.template = mline

        else:
            # TODO: protect { and } in comment parts of the card.
            tmpl = [] # part of template
            inpt = [] # input, meaningful parts of the card.
            if mline.split()[0][:2] == 'fc':
                # this is tally comment. It always in one line and is not delimited by & or $
                i = mline[:80]
                t = mline.replace(i, '{}', 1)
                inpt = [i]
                tmpl = [t]
            else:
                for l in self.lines:
                    if is_commented(l):
                        tmpl.append(l)
                    else:
                        # entries optionally delimited from comments by $ or &
                        d1 = l.find(' $') # requires that delimiters prefixed with space-
                        d2 = l.find(' &')
                        if -1 < d1 and -1 < d2:
                            # both & and $ in the line. Use the most left
                            d = min(d1, d2)
                        elif d1 == -1 and d2 == -1:
                            # no delimiters at all, whole line is meaningful except the new-line char
                            d = len(l) - 1
                        else:
                            # only one of delimiters is given.
                            d = max(d1, d2)
                        i = l[:d]
                        t = l[d:]
                        inpt.append(i)
                        tmpl.append(fmt_s(i) + t)
            self.input = inpt
            self.template = ''.join(tmpl)
        self.print_debug('get_input', 'ti')
        return

    def _protect_nums(self):
        """
        In the meaningful part of the card replace numbers that do not represent cell, surface or a cell parameter with some unused char.
        """

        inpt = '\n'.join(self.input)

        d = {}

        # in cell card:
        if self.ctype == CID.cell and 'like' not in inpt:
            d['~'] = [] # float values in cells

            tokens = inpt.replace('=', ' ').split()
            # material density
            cell, mat, rho = tokens[:3]
            if int(mat) != 0:
                for s in (cell, mat, rho):
                    inpt = inpt.replace(s, '~', 1)
                inpt = inpt.replace('~', cell, 1)
                inpt = inpt.replace('~', mat, 1)
                d['~'].append(rho)

            # imp and tmp parameters:
            for s in re_prm.findall(inpt):
                d['~'].append(s)
                inpt = inpt.replace(s, '~', 1)


        # replace repitition syntax in junks:
        sbl = re_rpt.findall(inpt)
        if sbl:
            for s in sbl:
                inpt = inpt.replace(s, '!', 1)
            d['!'] = sbl

        if self.ctype == CID.data and inpt.lstrip().lower()[0] == 'f' and inpt.lstrip()[1].isdigit():
            # this is tally card. Hide indexes in square brackets
            sbl = re_ind.findall(inpt)
            if sbl:
                for s in sbl:
                    inpt = inpt.replace(s, '|', 1)
                d['|'] = sbl

        self.input = inpt.split('\n')
        self.hidden = d

        self.print_debug('_protect_nums', 'ih')
        return

    def get_values(self):
        """
        Replace integers in the meaningfull part with format specifiers, and populate the `values` attribute.
        """
        self._protect_nums()
        if self.ctype == CID.cell:
            inpt, vt = _split_cell(self.input)
        elif self.ctype == CID.surface:
            inpt, vt = _split_surface(self.input)
        elif self.ctype == CID.data:
            inpt, vt, dtype = _split_data(self.input)
            self.dtype = dtype
        else:
            inpt = self.input
            vt = []

        self.input = inpt
        self.values = vt

        self.print_debug('get_values', 'iv')
        return

    def card(self, wrap=False):
        """
        Return multi-line string representing the card.
        """

        if self.input:
            # put values back to meaningful parts:
            inpt = '\n'.join(self.input)
            inpt = inpt.format(*map(lambda t: t[0], self.values))

            # put back hidden parts:
            for k, vl in self.hidden.items():
                for v in vl:
                    inpt = inpt.replace(k, v, 1)
            inpt = inpt.split('\n')

            if wrap:
                tparts = self.template.split('{}')[1:]
                newt = [''] # new template parts
                newi = [] # new input parts
                self.print_debug('card wrap=True', '')
                for i, t in zip(inpt, tparts):
                    self.print_debug('    ' + repr(i) + repr(t), '')
                    il = []
                    tl = [t]

                    while len(i.rstrip()) > 79:
                        # first try to shift to left
                        if i[:5] == ' '*5:
                            i = ' '*5 + i.lstrip()
                        if len(i.rstrip()) > 79:
                            # input i must be wrapped. Find proper place:
                            for dc in ' :':
                                k = i.rstrip().rfind(dc, 0, 75)
                                if k > 6:
                                    il.append(i[:k])
                                    tl.append('\n')
                                    i = '     ' + i[k:]
                                    self.print_debug('card wrap=True' + repr(il[-1]) + repr(i), '')
                                    break
                            else:
                                # there is no proper place to wrap.
                                self.print_debug('card wrap=True cannot wrap line ' + repr(i), '')
                                # raise ValueError('Cannot wrap card on line', self.pos)
                                warnings.warn('Cannot wrap card on line {}'.format(self.pos))
                                break
                        else:
                            # input i fits to one line. Do nothing.
                            pass

                    newt += tl
                    newi += il + [i]
                tmpl = '{}'.join(newt)
                inpt = newi
            else:
                tmpl = self.template

            card = tmpl.format(*inpt)
        else:
            card = self.template
        return card


    def remove_spaces(self):
        """
        Remove extra spaces from meaningful parts.
        """
        self.print_debug('before remove_spaces', 'i')
        if self.ctype in (CID.cell, CID.surface, CID.data):
            inpt = []
            for i in self.input:
                indented = i[:5] == ' '*5
                # leave only one sep. space
                i = ' '.join(i.split())
                i = i.strip()
                # spaces before/after some characters are not needed:
                for c in '):':
                    i = i.replace(' ' + c, c)
                for c in '(:':
                    i = i.replace(c + ' ', c)
                if indented:
                    i = ' '*5 + i
                inpt.append(i)
                self.print_debug(i, '')
            self.input = inpt
            self.print_debug('after remove_spaces', 'i')
        return

    def apply_map(self, f):
        """
        Replace Ni in self.values by Mi = f(Ni, Ti).
        """
        self.print_debug('before apply_map', 'v')

        # u and fill should be renumberd in the same way, but types
        # must remain different, to let explicit u=0
        # self.values = map(lambda t: (f(t[0], t[1]), t[1]), self.values)
        newvals = []
        for t in self.values:
            if t[1] == 'fill':
                t1 = 'u'
            else:
                t1 = t[1]
            newvals.append((f(t[0], t1), t[1]))
        self.values = newvals
        self.print_debug('after apply_map', 'v')
        return



def _split_cell(input_):
    """
    Replace integers in the meaningful parts of a cell card with format specifiers,
    and return a list of replaced values together with their types.

    """

    # meaningful parts together. Originally, they cannot have \n chars, since
    # all of them should land to the card template, therefore, after all
    # entries are replaced with format specifiers, it can be split back to a
    # list easily at \n positions.
    inpt = '\n'.join(input_)

    vals = [] # list of values
    fmts = [] # value format. It contains digits, thus will be inserted into inpt later.
    tp = '_'  # temporary placeholder for format specifiers
    if 'like ' in inpt.lower():
        # raise NotImplementedError()
        warnings.warn('Parser for "like but" card, found on line {}, is not implemented'.format(self.pos))
    else:
        # cell card has usual format.


        t = inpt.split()

        # Get cell name
        js = t.pop(0)
        inpt = inpt.replace(js, tp, 1)
        vals.append((int(js), 'cel'))
        fmts.append(fmt_d(js))

        # get material and density.
        # Density, if specified in cells card, should be allready hidden
        ms = t.pop(0)
        inpt = inpt.replace(ms, tp, 1)
        vals.append((int(ms), 'mat'))
        fmts.append(fmt_d(ms))

        # Get geometry and parameters blocks I assume that geom and param
        # blocks are separated by at least one space, so there will be an
        # element in t starting with alpha char -- This will be the first token
        # from the param block.
        geom = []
        parm = []
        while t:
            e = t.pop(0)
            if e[0].isalpha():
                parm = [e] + t
                break
            else:
                geom.append(e)

        # replace integer entries in geom block:
        for s in re_int.findall(' '.join(geom)):
            # s is a surface or a cell (later only if prefixed by #)
            t = 'cel' if s[0] == '#' else 'sur'
            s = s if s[0].isdigit() else s[1:]
            f = fmt_d(s)
            inpt = inpt.replace(s, tp, 1)
            vals.append((int(s), t))
            fmts.append(f)

        # replace values in parameters block. Values are prefixed with = or space(s)
        # Note that tmp and imp values must be hidden
        t = ' '.join(parm).replace('=', ' ').split() # get rid of =.
        while t:
            s = t.pop(0)
            parsed = False
            if s.lower() == 'u' or 'fill' in s.lower():
                # I assume that only one integer follows.
                vs = t.pop(0)
                vv = int(vs)
                vf = fmt_d(vs)

                # TODO fill value can be an array
                vt = 'fill' if 'fill' in s.lower() else 'u' # this distinguish between fill and u is necessary to put explicit u=0 to cells filled with some other universe.
                # vt = 'u'
                parsed = True
                # warn if there is possibility for an array following the fill keyword:
                if 'fill' is s.lower() and 'lat' in ''.join(parm).lower():
                    print "WARNING: fill keyword followed by an array cannot be parsed"

            if parsed:
                inpt = inpt.replace(vs, tp, 1)
                vals.append((vv, vt))
                fmts.append(vf)

        # replace '_' with fmts:
        for f in fmts:
            inpt = inpt.replace(tp, f, 1)

        return inpt.split('\n'), vals


def _split_surface(input_):
    """
    Similar to _split_cell(), but for surface cards.
    """
    inpt = '\n'.join(input_)
    t = inpt.split()

    vals = [] # like in split_cell()
    fmts = []
    tp = '_'

    # get surface name:
    js = t.pop(0)
    if not js[0].isdigit():
        js = js[1:]
    inpt = inpt.replace(js, tp, 1)
    vals.append((int(js), 'sur'))
    fmts.append(fmt_d(js))

    # get TR or periodic surface:
    ns = t.pop(0)
    if ns[0].isdigit():
        # TR is given
        inpt = inpt.replace(ns, tp, 1)
        vals.append((int(ns), 'tr'))
        fmts.append(fmt_d(ns))
    elif ns[0] == '-':
        # periodic surface
        ns = ns[1:]
        inpt = inpt.replace(ns, tp, 1)
        vals.append((int(ns), 'sur'))
        fmts.append(fmt_d(ns))
    elif ns[0].isalpha():
        # ns is the surface type
        pass
    else:
        raise ValueError(input_, inpt, ns)

    for f in fmts:
        inpt = inpt.replace(tp, f, 1)

    return inpt.split('\n'), vals

def _get_int(s):
    r = ''
    for c in s:
        if r and c.isalpha():
            break
        elif c.isdigit():
            r += c
    return r

def _split_data(input_):
    inpt = '\n'.join(input_)
    t = inpt.split()

    vals = []
    fmts = []
    tp = '_'

    if 'tr' in t[0][:3].lower():
        # TRn card
        dtype = 'TRn'
        ns = _get_int(t[0])
        inpt = inpt.replace(ns, tp, 1)
        vals.append((int(ns), 'tr'))
        fmts.append(fmt_d(ns))
    elif t[0][0].lower() == 'm' and 'mode' not in t[0].lower():
        # Mn, MTn or MPNn card
        ms = _get_int(t[0])
        inpt = inpt.replace(ms, tp, 1)
        vals.append((int(ms), 'mat'))
        fmts.append(fmt_d(ms))
        # additional tests to define data card type:
        if t[0][1].isdigit():
            dtype = 'Mn'
        elif t[0][1].lower() == 't':
            dtype = 'MTn'
        elif t[0][1].lower() == 'p':
            dtype = 'MPNn'
    elif t[0][0].lower() == 'f' and t[0][1].isdigit():
        # FN card
        dtype = 'Fn'
        ns = _get_int(t[0]) # tally number
        inpt = inpt.replace(ns, tp, 1)
        vals.append((int(ns), 'tal'))
        fmts.append(fmt_d(ns))

        # define type of integers by tally type:
        nv = int(ns[-1])
        if nv in [1, 2]:
            typ = 'sur'
        elif nv in [4, 6, 7, 8]:
            typ = 'cel'
        else:
            typ = ''

        if typ:
            # Lattice indices, surrounded by square brakets must allready be hidden

            # Special treatment, if tally has 'u=' syntax.
            hasu = 'u' in inpt.lower() and '=' in inpt.lower()
            # find all integers -- they are cells or surfaces
            for s in re_int.findall(inpt):
                ss = s[1:]
                tpe = typ
                if hasu:
                    # ss can be universe. To distinguish this, one needs to look
                    # back in previous cheracters in c.
                    i1 = inpt.rfind(tp)
                    i2 = inpt.find(ss)
                    part = inpt[i1:i2]
                    while ' ' in part:
                        part = part.replace(' ', '')
                    if part[-2:].lower() == 'u=':
                        tpe = 'u'
                inpt = inpt.replace(ss, tp, 1)
                vals.append((int(ss), tpe))
                fmts.append(fmt_d(ss))
    else:
        dtype = None

    for f in fmts:
        inpt = inpt.replace(tp, f, 1)

    return inpt.split('\n'), vals, dtype





def is_commented(l):
    """
    Return True if l is a commented line.
    """
    res = False

    # remove newline chars at the end of l:
    l = l.splitlines()[0]
    if 'c ' in l[0:6].lstrip().lower():
        res = True
        #print 'is_com "c "',
    elif 'c' == l.lower():
        res = True
        #print 'is_com "c"',
    #print 'is_com', res
    return res

def is_fc_card(l):
    """
    Return true, if line l is tally comment cards, fcN
    """
    return l.lstrip().lower()[:2] == 'fc'

def is_blankline(l):
    """
    Return True, if l is the delimiter blank line.
    """
    return l.strip() == ''


def get_cards(inp, debug=None):
    """
    Iterable, return (str, Itype), where str is a list of lines representing a
    card, and Itype is the type of the card (i.e. message, cell, surface or  data)

    inp -- is the filename.
    """

    def _yield(card, ct, ln):
        return Card(card, ct, ln, debug)

    cln = 0 # current line number. Used only for debug
    with open(inp, 'r') as f:
        # define the first block:
        # -----------------------

        # Next block ID
        ncid = 0 # 0 is not used in card ID dictionary CID.

        # Parse the 1-st line. It can be message, cell or data block.
        l = f.next()
        cln += 1
        kw = l.lower().split()[0]
        if 'message:' == kw:
            # read message block right here
            res = [l]
            while not is_blankline(l):
                l = f.next()
                cln += 1
                res.append(l)
            yield _yield(res, CID.message, cln-1)  # message card
            yield _yield(l, CID.blankline, cln)      # blank line
            l = f.next()
            cln += 1
            ncid = CID.title
        elif 'continue' == kw:
            # input file for continue job. Contains only data block.
            ncid = CID.data
        else:
            ncid = CID.title
        if ncid == CID.title:
            # l contains the title card
            yield _yield([l], ncid, cln)
            ncid += 1

        # read all other lines
        # --------------------

        # Line can be a continuation line in the following cases:
        #   * all lines in the message block, i.e. before the blank line delimiter
        #   * if line starts with 5 or more spaces,
        #   * if previous line ends with & sign.
        # Thus, the role of the current line (continuation or not) can be
        # defined by the line itself (5 spaces), or by previous lines (message
        # block or & sign). This can lead to inconsistency, when previous line
        # is delimited by &, but is followed by the blank line delimiter.  in
        # this case (rather theretical), blank line delimiter (as appeared more
        # lately) delimites the card from the previous line.
        cf = False  # continuation line flag. Set to true only when prev. line contains &.

        # Comment lines (CL) can be between cards or inside them. CL between two cards are yielded as block of comments
        # (although usually, CL are used to describe cards that follow them).
        # CL inside a card will belong to the card.

        card = []  # card is a list of lines.
        cmnt = []  # list of comment lines.
        for l in f:
            cln += 1
            if is_blankline(l):
                # blank line delimiter. Stops card even if previous line contains &
                if card:
                    # card can be empty, for example, when several empty lines are at the end of file
                    yield _yield(card, ncid, cln - len(card) - len(cmnt))
                if cmnt:
                    yield _yield(cmnt, CID.comment, cln - len(cmnt))
                    cmnt = []
                yield _yield(l, CID.blankline, cln)
                ncid += 1
                card = []
            elif l[0:5] == '     ' or cf:
                # l is continuation line.
                if cmnt:
                    card += cmnt # previous comment lines, if any, belong to the current card.
                    cmnt = []
                card.append(l)
                cf = l.find('&', 0, 81) > -1
            elif is_commented(l):
                # l is a line comment. Where it belongs (to the current card or to the next one),
                # depends on the next line, therefore, just store temorarily.
                cmnt.append(l)
            else:
                # l is the 1-st line of a card. Return previous card and comments
                if card:
                    yield _yield(card, ncid, cln - len(card) - len(cmnt))
                if cmnt:
                    yield _yield(cmnt, CID.comment, cln - len(cmnt))
                    cmnt = []
                card = [l]

                cf = not is_fc_card(l) and l.find('&', 0, 81) > -1 # if tally comment card, i.e. started with fc, the & character does not mean continuation.
        if card:
            yield _yield(card, ncid, cln - len(card) - len(cmnt))
        if cmnt:
            yield _yield(cmnt, CID.comment, cln - len(cmnt))




if __name__ == '__main__':
    pass
