#!/usr/bin/env python

from __future__ import print_function

import argparse as ap
import sys
from math import pi as Pi
import os.path
from numjuggler import numbering as mn
from numjuggler import parser as mp
from numjuggler import ri_notation as rin
from numjuggler import string_cells as stc
from numjuggler import likefunc as lf
from numjuggler import version

try:
    import pirs.mcnp.mctal.Mctal as Mctal, Vector3, Material
except:
    Material = None
    Mctal = None
    Vector3 = None


def multiline(lines, prefix=''):
    return prefix + ('\n' + prefix).join(lines)


def tr2str(pl, fmt1='{:12.9f}', fmte='{:16.8e}'):
    """
    Compact format for tr card.
    """
    r = ['tr{:<}']
    for p in pl:
        if p == 0:
            ps = '0'
        elif p == -1:
            ps = '-1'
        elif p == 1:
            ps = '1'
        elif -10 < p < 10:
            ps = fmt1.format(p)
        else:
            ps = fmte.format(p)

        # Remove unnecessary characters
        ps = ps.replace('e-0', 'e-')
        ps = ps.replace('e+0', 'e+')
        ps = ps.replace(' ', '')

        if len(r[-1]) + len(ps) > 80:
            r.append('\n    ')
        r[-1] += ' ' + ps
    return ''.join(r)


# help messages already wrapped:
help_c = """
Cell number increment. If an integer is given, it is added to all cell numbers
(negative entries are valid as well). If "i" is given, cell numbers are
replaced by their sequence numbers, in the order as they appear in the input
file (the 1-st cell becomes number 1, etc)
"""[1:]  # here I remove the 1-st newline

help_s = '{} number increment, similar to "-c"'

help_m = """
File, containing descrption of mapping. When specified, options "-c", "-s", "-m"
and "-u" are ignored.
"""[1:]

descr = """
Renumber cells, surfaces, materials and universes in MCNP input file. The
original MCNP input file name must be given as command line option, the modified
MCNP input file is written to std.out."""[1:]

epilog = """
Specify 'mode', 'map', 'limitations', or the mode name after -h for additional
help.
"""

modes = ('renum', 'info', 'wrap', 'uexp', 'rems', 'remc', 'remh', 'remrp', 'minfo',
         'split', 'mdupl', 'matan', 'sdupl', 'msimp', 'extr',
         'nogq', 'nogq2', 'count', 'nofill', 'matinfo', 'uinfo',
         'impinfo', 'fillempty', 'sinfo', 'vsource',
         'tallies', 'addgeom', 'merge', 'remu', 'zrotate',
         'annotate', 'getc', 'mnew', 'combinec', 'cdens')


def main(args=sys.argv[1:]):
    p = ap.ArgumentParser(prog='numjuggler', description=descr, epilog=epilog)
    p.add_argument('--version', action='version',
                   version='%(prog)s {}'.format(version))
    p.add_argument('inp', help='MCNP input file')
    p.add_argument('-c', help=help_c,
                   type=str,
                   default='0')
    p.add_argument('-s', help=help_s.format('Surface'),
                   type=str,
                   default='0')
    p.add_argument('-m', help=help_s.format('Material'),
                   type=str,
                   default='0')
    p.add_argument('-u', help=help_s.format('Universe'),
                   type=str,
                   default='0')
    p.add_argument('-t', help=help_s.format('Transformation'),
                   type=str,
                   default='0')
    p.add_argument('-opt', help='remrp option. "cc" set all cells as complex cell; "all" remove all redundant parentheses ',
                   type=str,
                   choices=['nochg','cc','all'],
                   default='nochg')
    p.add_argument('-all', help='remrp option. All redundant parentheses are removed',
                   action='store_true')
    p.add_argument('--map', help=help_m,
                   type=str,
                   default='')
    p.add_argument('--mode', help='Execution mode, "renum" by default',
                   type=str,
                   choices=modes,
                   default='renum')
    p.add_argument('--debug', help='Additional output for debugging',
                   action='store_true')
    p.add_argument('--preservetabs',
                   help='Do not convert tabs to spaces. By default tabs are replaced with spaces according to MCNP5 rules (User''s manual Vol. II p. 1-3)',
                   action='store_true')
    p.add_argument('--log', help='Log file.',
                   type=str,
                   default='')

    # parse help option in another parser:
    ph = ap.ArgumentParser(add_help=False)
    ph.add_argument('-h', help='Print help and exit',
                    nargs='?',
                    default='',
                    const='gen')
    harg, clo = ph.parse_known_args(args)
    if harg.h:
        if harg.h == 'gen':
            p.print_help()
        else:
            # try to read correspondent file from help folder
            try:
                import numjuggler as nj
                dir1 = os.path.split(nj.__file__)[0]  # remove filename
                dir1 = os.path.split(dir1)[0]         # remove the most deep dir
                hlp = os.path.join(dir1, 'help/{}.rst'.format(harg.h))
                print('Reading help from {}'.format(hlp))
                print(open(hlp).read())
            except Exception as e:
                print('Cannot read help file for "{}"'.format(harg.h))

        # elif harg.h in dhelp:
        #     print(dhelp[harg.h])
        # else:
        #     import numjuggler as nj
        #     # TODO use nj.__file__ to read from help folder.

        #     print('No help for ', harg.h)
        #     print('Available help options: ', dhelp_keys)
    else:
        args = p.parse_args(clo)
        if args.debug:
            # args.inp can be a path with folders. Ensure that the prefix
            # 'debug.juggler' is added to the base filename only.
            d, f = os.path.split(args.inp)
            debug_file_name = os.path.join(d, 'debug.juggler.' + f)
            # print
            # print 'Debug info written to ', debug_file_name
            # print
            debuglog = open(debug_file_name, 'w')
            print('command line arguments:', args, file=debuglog)
        else:
            debuglog = None

        # process input file only once:
        cards = list(mp.get_cards(args.inp,
                                  debuglog,
                                  preservetabs=args.preservetabs))

        if args.mode == 'info':
            indent = ' '*8
            for c in cards:
                c.get_values()
            d = mn.get_numbers(cards)

            if args.debug:
                types = sorted(d.keys())
            else:
                types = ['cel', 'sur', 'mat', 'u', 'tal', 'tr']
            for t in types:
                if t[0] != '#':  # for meaning of '#' see parser.
                    nset = set(d.get(t, []))
                    print('-' * 40, t, len(nset))
                    print('-' * 20, t, ' list', end='')
                    print(' '.join(map(str, rin.shorten(sorted(nset)))))
                    rp = None
                    for r1, r2 in mn._get_ranges_from_set(nset):
                        print('{}{:>3s}'.format(indent, t[0]), end='')
                        if r1 == r2:
                            rs = ' {}'.format(r1)
                        else:
                            rs = ' {} -- {}'.format(r1, r2)
                        if rp is not None:
                            fr = '{}'.format(r1 - rp - 1)
                        else:
                            fr = ''
                        ur = '{}'.format(r2 - r1 + 1)
                        print('{:<30s} {:>8s} {:>8s}'.format(rs, ur, fr))
                        rp = r2
        elif args.mode == 'remh':
            stc.remove_hash(cards,args.log)
            for c in cards:
               if c.cstrg :   # strg: flags setting if card has been modified with remove
                  c.get_input()
                  print(c.card(True), end='')
               else:
                  print(c.card(), end='')

        elif args.mode == 'remrp':
            print_log = False
            if args.log != '' :
               flog = open(args.log,'w')
               flog.write('      Cell :  Parentheses removed\n')
               print_log = True
            for c in cards:
               if c.ctype == mp.CID.cell:
                  cardstr = stc.cell_card_string(''.join(c.lines))
                  cardstr.geom.remove_redundant(remopt=args.opt)
                  c.lines = cardstr.get_lines()
                  c.get_input()
                  if print_log:
                     if cardstr.geom.removedp :
                       cname = cardstr.headstr.split()[0]
                       if (cardstr.geom.removedp[0] != cardstr.geom.removedp[1] ):
                           flog.write(' {:>9s} : unbalanced\n'.format(cname))
                       elif ( args.opt == 'nochg' and cardstr.geom.removedp[0] == 0) :
                          flog.write(' {:>9s} : nochg\n'.format(cname))
                       else:
                          flog.write(' {:>9s} : {:>5}\n'.format(cname,cardstr.geom.removedp[0]))
                  print(c.card(True), end='')
               else:
                  print(c.card(), end='')

        elif args.mode == 'ext':
            # output list of cells for ext:n card
            for c in cards:
                c.get_values()
            d = mn.get_numbers(cards)


        elif args.mode == 'cdens':
            from .mapparsers import cdens
            # Change density of cells, specified in the map file. Map file
            m, mdef = cdens(args.map)

            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    modified = False
                    for tr in m.keys():
                        t, r = tr
                        if t == 'c' and  c.name in r:
                            dorig = c.get_d()
                            coef, fmt = m[tr]
                            dnew = dorig * coef
                            c.set_d(fmt.format(dnew))
                            modified = True
                        if t == 'm' and c.get_m() in r:
                            dorig = c.get_d()
                            coef, fmt = m[tr]
                            dnew = dorig * coef
                            c.set_d(fmt.format(dnew))
                            modified = True
                    if not modified and mdef:
                        # If no rules to modify density found, apply the
                        # default:
                        dnew = c.get_d()
                        for t, (val, fmt) in mdef.items():
                            dnew *= val
                        c.set_d(fmt.format(dnew))
                print(c.card(), end='')


        elif args.mode == 'tallies':
            # New version: tally number and universes should be specified in the
            # format string passed via -m argument.  -m must be present and have
            # form: 'f4:n (u4 < u5)', where uN -- placeholders for lists of
            # cells that belong to universe N. Usual cell numbers can be used
            # as well.

            import re
            r = re.compile(r'(u)(\d+)')

            csets = {}
            ulst = []
            fmt = args.m[:]
            for s in r.findall(args.m):
                ss = s[0] + s[1]
                u = int(s[1])
                csets[u] = set()
                fmt = fmt.replace(ss, '{' + ss + '}', 1)
                ulst += [u]

            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.cell:
                    cu = c.get_u()
                    if cu is None:
                        cu = 0
                    if cu in csets:
                        csets[cu].add(c.name)
                elif c.ctype == mp.CID.surface:
                    break

            farg = {}
            for k, v in list(csets.items()):
                farg['u' + str(k)] = ' '.join(map(str, rin.shorten(sorted(v))))

            # Tally card
            print(fmt.format(**farg))

            # SD card. Requires tally number and number of cells
            nt = fmt.split(':')[0][1:]
            nc = len(csets[ulst[0]])  # number of cells
            print('sd{} 1 {}r'.format(nt, nc - 1))
            print('fc{} '.format(nt), end='')
            for u in ulst:
                print(len(csets[u]), end='')
            print()

        elif args.mode == 'addgeom':
            # add stuff to geometry definition of cells.

            # Get info from the --map file:
            extr = {}
            rem = set()
            if ',' in args.m:
                ds1, ds2 = args.m.split(',')
            else:
                ds1 = ''
                ds2 = ''
            if args.map:
                for l in open(args.map):
                    l = l.strip()
                    if l:
                        tokens = l.split(None, 1)
                        if len(tokens) == 1:
                            # special case: cell c should be removed from the
                            # resulting input.
                            rem.add(int(tokens[0]))
                        else:
                            c, s = tokens
                            c = int(c)
                            if ',' in s:
                                s1, s2 = s.split(',')
                                s1 = ' ' + s1.strip() + ' '
                                s2 = ' ' + s2.strip() + ' '
                            else:
                                s1 = ' ' + s.strip() + ' '
                                s2 = ''
                            extr[c] = (s1, s2)

            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    c.geom_prefix = ds1
                    c.geom_suffix = ds2
                    if c.name in extr:
                        s1, s2 = extr[c.name]
                        c.geom_prefix = s1
                        c.geom_suffix = s2
                    if c.name not in rem:
                        print(c.card(), end='')
                else:
                    print(c.card(), end='')

        elif args.mode == 'merge':
            # Merge treats models as the main one and an additional one.  Title
            # of the resulting model -- from the main model, or user specified
            # by -t option.  Blocks of the additional model are denoted by
            # user-specified comments, or by "c numjuggler title"

            # get cards of the second input
            cards2 = list(mp.get_cards(args.m, debuglog))

            blk1 = mp.get_blocks(cards)
            blk2 = mp.get_blocks(cards2)

            # The first input is used as the main one.  Blocks of the second
            # input are inserted at the end, surrounded by comments.

            # Message -- from the 1-st input if exists, otherwise -- from the
            # second.
            if mp.CID.message in blk1:
                mb = blk1[mp.CID.message]
            elif mp.CID.message in blk2:
                mb = blk2[mp.CID.message]
            else:
                mb = []
            if mb:
                for c in mb:
                    print(c.card(), end='')
                print('')

            # Title:
            if args.t == "0":
                # default one. Use title of the main input
                t = blk1[mp.CID.title][0].card()[:-1]
            else:
                t = args.t
            print(t)

            # Comments, denoting blocks of the additional model:
            if args.c == "0":
                # default. Use the additional model's title.  Assumed that both
                # inputs have title cards, i.e. not continuation input files.
                t2 = blk2[mp.CID.title][0]
                # emphasize second title
                cmnt = 'c {} {} cards ' + '"{}"'.format(t2.card()[:-1])
            else:
                cmnt = 'c {} {} cards ' + args.c

            # Cells, surfaces and data:
            for t in [mp.CID.cell, mp.CID.surface, mp.CID.data]:
                for c in blk1[t]:
                    print(c.card(), end='')

                if t in blk2 and blk2[t]:
                    # First check if blk2 actually contains any cards:
                    flg = False
                    for c in blk2[t]:
                        if c.ctype == t:
                            flg = True
                            break
                    if flg:
                        print(cmnt.format('start', mp.CID.get_name(t)))
                        for c in blk2[t]:
                            print(c.card(), end='')
                        print(cmnt.format('end', mp.CID.get_name(t)))

                if t != mp.CID.data:
                    # do not add empty line after data block
                    print('')

        elif args.mode == 'uexp':
            if args.u == "0":
                N = " u=0 "
            else:
                N = args.u

            # Define function that filters cells to be checked:
            if args.c == "0":
                # default. Check all cells.
                def cfunc(n):
                    return True
            elif "!" in args.c:
                # Check only cells not mentioned in -c
                cset = set(rin.expand(args.c.replace("!", " ").split()))

                def cfunc(n):
                    return n not in cset
            else:
                # Check only cells  mentioned in -c
                cset = set(rin.expand(args.c.replace("!", " ").split()))

                def cfunc(n):
                    return n in cset

            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    if (cfunc(c.name) and
                       'u' not in [t[1] for t in c.values]):
                        c.input[-1] += N  # ' u=0'
                print(c.card(), end='')

        elif args.mode == 'wrap':
            for c in cards:
                print(c.card(wrap=True), end='')

        elif args.mode == 'rems':
            for c in cards:
                c.remove_spaces()
                print(c.card(), end='')

        elif args.mode == 'remc':
            for c in cards:
                if c.ctype == mp.CID.comment:
                    continue
                print(c.card(), end='')

        elif args.mode == 'split':
            blocks = mp.get_blocks(cards)
            for k, cl in list(blocks.items()):
                if cl:
                    i = mp.CID.get_name(k)
                    with open(args.inp + '.{}{}'.format(k, i), 'w') as fout:
                        for c in cl:
                            print(c.card(), end='', file=fout)

                    # create file with blank line delimiter
                    if k in (mp.CID.cell, mp.CID.surface):
                        fout = open(args.inp + '.{}z'.format(k), 'w')
                        print(' ', file=fout)
                        fout.close()

        elif args.mode == 'matan':
            # Compare pairwise mateiral cards. Two materials are compared by
            # their string representation

            from pirs.mcnp import Material
            # read all material cards and convert to string representation
            sd = {}
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.data and c.dtype == 'Mn':
                    m = Material.parseCard(c)
                    m.remove_duplicates()
                    m.normalize(1.0)
                    s = m.card(sort=True, suffixes=False, comments=False)
                    if s not in sd:
                        sd[s] = [m.name]
                    else:
                        sd[s].append(m.name)

            # analyse material cards:
            i = 1
            for s, m in list(sd.items()):
                print(i, m)
                i += 1

        elif args.mode == 'mdupl':
            # remove duplicate material cards, if they are equal.

            mset = set()
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.data and c.dtype == 'Mn':
                    if c.values[0][0] not in mset:
                        print(c.card(), end='')
                        mset.add(c.values[0][0])
                else:
                    print(c.card(), end='')

        elif args.mode == 'mnew':
            # read from map definition of new materials in terms of existing
            # materials, and add new to the modified input.

            # Read new material definitions from the map file:
            dd = {} # definition dictionary
            rms = set() # reference materials set
            with open(args.map) as fmap:
                for l in fmap:
                    tl = l.split()
                    rml = map(int, tl[1::3])
                    dd[tl[0]] = zip(rml,
                                    map(float, tl[2::3]),
                                    map(float, tl[3::3]))
                    rms.update(rml)

            # read reference materials and create Materials
            assert Material is not None,  "pirs Material class is not imported"
            rmd = {}
            for c in cards:
                if c.ctype == mp.CID.data:
                    c.get_values()
                    if c.dtype == 'Mn' and c.name in rml:
                        m = Material.parseCard(c)
                        m.name = 'm{} from {}'.format(c.name, args.inp)
                        rmd[c.name] = m

            # create new materials
            for n, d in dd.items():
                r = [] # recipe
                for i in d:
                    r.append(rmd[i[0]])
                    r.append((i[1] * i[2], 2))
                m = Material(*r)
                print('\nc '.join(m.report().splitlines()))
                print(m.card().format(n))


        elif args.mode == 'sdupl':
            # report duplicate (close) surfaces.
            # dict of unique surafces
            us = {}

            #  surface types coefficients that can only be proportional
            pcl = {
                    'p': (0,),
                    'sq': (0, 7),
                    'gq': (0,)
                    }
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.surface:
                    # compare this surface with all previous and if unique, add
                    # to dict
                    if c.stype not in us.keys():
                        us[c.stype] = {}
                    ust = us[c.stype]
                    for sn, s in list(ust.items()):
                        if mp.are_close_lists(s.scoefs, c.scoefs,
                                              pci=pcl.get(c.stype, [])):
                            # If c is close to s, print s instead
                            s.values[0] = (c.values[0][0], s.values[0][1])
                            print(s.card(), end='')
                            s.values[0] = (sn, s.values[0][1])
                            break
                    else:
                        # add c to us:
                        cn = c.values[0][0]  # surface name
                        ust[cn] = c
                        print(c.card(), end='')
                        # print 'is unique'
                else:
                    print(c.card(), end='')

        elif args.mode == 'msimp':
            # simplify material cards
            for c in cards:
                if c.ctype == mp.CID.data:
                    c.get_values()
                    if c.dtype == 'Mn':
                        inp = []
                        inp.append(c.input[0].replace('}',
                                                      '} 1001 1.0 $ msimpl ', 1))
                        for i in c.input[1:]:
                            inp.append('c msimpl ' + i)
                        c.input = inp
                print(c.card(), end='')

        elif args.mode == 'remu':
            if args.u[0] == '!':
                # -u option starts with !. In this case, remove all other
                # universes.
                iflag = True
                args.u = args.u[1:]
            else:
                iflag = False
            # uref = set(map(int, args.u.split()))
            uref = set(map(int, rin.expand(args.u.split())))
            cset = set()
            sset = set()
            mset = set()
            if args.map != '':
                # read cells to remove from --map file
                for l in open(args.map):
                    for v in l.split():
                        cset.add(int(v))
            if args.c != '0':
                le = rin.expand(args.c.split())
                for v in le:
                    cset.add(int(v))

            # get card values
            uset = set()  # in case universes require inversion
            for c in cards:
                if c.ctype in (mp.CID.cell, mp.CID.surface, mp.CID.data):
                    c.get_values()
                    uset.add(c.get_u())
            if iflag:
                uref = uset.difference(uref)
                # None can be added to uref when no universe is specified
                # explicitly (i.e. for all u0 cells)
                uref.discard(None)

            # Universe number that is used to replace all deleted universes
            # in hte FILL options
            # newfill = sorted(uref)[0]

            # get list of cells to be removed
            # and list of surfaces to be preserved
            for c in cards:
                if c.ctype == mp.CID.cell:
                    if c.get_u() in uref:
                        cset.add(c.name)
                    elif c.name not in cset:
                        # collect surfaces needed for other cells
                        for v, t in c.values:
                            if t == 'sur':
                                sset.add(v)
                            if t == 'mat':
                                mset.add(v)

            # Prepare additional lines to be added to cell and surface blocks:
            newcell = 'c '
            newsurf = 'c '
            if args.m != '0':   # -c is already used!
                newcell = args.m
            if args.s != '0':
                newsurf = args.s

            prevctype = None
            for c in cards:
                if c.ctype == mp.CID.cell and c.name in cset:
                    pass
                elif c.ctype == mp.CID.surface and c.name not in sset:
                    pass
                elif (c.ctype == mp.CID.data and
                      c.dtype == 'Mn' and
                      c.values[0][0] not in mset):
                    print('c qqq', repr(c.values[0][0]))
                    pass
                else:
                    # check that cell card does not depend on one of cset:
                    if c.get_refcells():
                        for i in range(len(c.values)):
                            v, t = c.values[i]
                            if t == 'cel' and v in cset:
                                c.values[i] = ('___', 'cel')
                    # If the cell is filled with a universe to delete,
                    # change its fill to newfill:
                    # if c.get_f() in uref:
                    #     c.get_f(newv = newfill)

                    # Insert additional cell
                    if prevctype == mp.CID.cell and c.ctype == mp.CID.blankline:
                        print(newcell)

                    print(c.card(), end='')

                    # Insert additional surface
                    if prevctype == mp.CID.cell and c.ctype == mp.CID.blankline:
                        print(newsurf)

                if c.ctype != mp.CID.comment:
                    prevctype = c.ctype

            print('c sset', ' '.join(map(str, rin.shorten(sorted(sset)))))
            print('c uref', ' '.join(map(str, rin.shorten(sorted(uref)))))
            # print dummy universes, just in case they are needed
            print()
            l = len(str(max(uref)))
            f = '{{0:0{}d}}'.format(l)
            for u in sorted(uref):
                s = f.format(u)
                print('dummy_prefix{0} 0 dummy_surface u={0}'.format(s))
            print('c mset', ' '.join(map(str, rin.shorten(sorted(mset)))))

        elif args.mode == 'combinec':
            # Combine cells, listed in -c flag.

            # Get cells to be combined from command line parameter
            clst1 = map(int, rin.expand(args.c.split()))

            # Get the cell geometry
            d = {}
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    if c.name in clst1:
                        d[c.name] = c
                if d and c.ctype == mp.CID.blankline:
                    break

            new_card = d[clst1[0]]
            new_card.geom_prefix = ' ('
            new_card.geom_suffix = ') '
            for n in clst1[1:]:
                g = d[n].get_geom()
                g = ' '.join(g.splitlines())
                new_card.geom_suffix += '({}) '.format(g)


            # Print out the new file
            for c in cards:
                if c.ctype == mp.CID.cell:
                    if c.name in clst1[1:]:
                        print('c ' + '\nc '.join(c.card().splitlines()))
                    else:
                        print(c.card(), end='')
                else:
                    print(c.card(), end='')


        elif args.mode == 'zrotate':

            assert  Vector3 is not None, "pirs Vector3 class is not imported"
            ag = float(args.c)    # in grad
            ar = ag * Pi / 180.   # in radians

            # new transformation number:
            trn = args.t
            trcard = '*tr{} 0 0 0 {} {} 90   {} {} 90   90 90 0'.format(
                trn, ag, ag-90, 90+ag, ag)
            # change all tr cards and surface cards:
            for c in cards:
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    # Surface parameters are not parsed, only surface number and
                    # transformation.
                    if len(c.values) == 1:
                        # surface has no transformation. Add the new one
                        inpt = '\n'.join(c.input)
                        inpt = inpt.replace('} ', '} ' + trn + ' ', 1)
                        c.input = inpt.split('\n')

                if c.ctype == mp.CID.data:
                    c.get_values()
                    if c.dtype == 'TRn':
                        # put new tr card just before the 1-st tr card in the
                        # input:
                        if trcard:
                            print(trcard)
                            trcard = None
                        # apply changes, assuming that tr card contains all 12
                        # entries:
                        o = Vector3(car=[v[0] for v in c.values[1:4]])
                        o.t += ar
                        c.values[1] = (o.x, 'float')
                        c.values[2] = (o.y, 'float')
                        c.values[3] = (o.z, 'float')

                        def e1(v):
                            return v[0]
                        if c.unit == '':
                            # rotation matrix contains cos
                            b1 = Vector3(car=list(map(e1, c.values[4:7])))
                            b2 = Vector3(car=list(map(e1, c.values[7:10])))
                            b3 = Vector3(car=list(map(e1, c.values[10:13])))
                            b1.t += ar
                            b2.t += ar
                            b3.t += ar
                            c.values[4] = (b1.x, 'float')
                            c.values[5] = (b1.y, 'float')
                            c.values[6] = (b1.z, 'float')
                            c.values[7] = (b2.x, 'float')
                            c.values[8] = (b2.y, 'float')
                            c.values[9] = (b2.z, 'float')
                            c.values[10] = (b3.x, 'float')
                            c.values[11] = (b3.y, 'float')
                            c.values[12] = (b3.z, 'float')
                        else:
                            # rotation matrix contains angles in grad.
                            b1, b2, b3, b4, b5, b6, b7, b8, b9 = list(map(e1, c.values[4:13]))

                            # Assume that it already describes rotation around z
                            # axis
                            assert (b3 == 90 and b6 == 90 and b7 == 90 and
                                    b8 == 90 and b9 == 0)

                            b1 += ag
                            b2 += ag
                            b4 += ag
                            b5 += ag
                            c.values[4] = (b1, 'float')
                            c.values[5] = (b2, 'float')
                            c.values[7] = (b4, 'float')
                            c.values[8] = (b5, 'float')

                print(c.card(), end='')

        elif args.mode == 'annotate':
            # Read text from map file, add "c" to each line and put after the
            # title.
            if args.c == "0":
                # default commenting string:
                cs = 'c '
            else:
                # user-specified commenting string:
                cs = args.c

            txt = [cs + l for l in open(args.map).readlines()]

            for c in cards:
                print(c.card(), end='')
                if c.ctype == mp.CID.title:
                    for l in txt:
                        print(l, end='')   # readlines() method returns lines with \n

        elif args.mode == 'getc':
            # Extract comments that take more than 10 lines:
            if args.c != "0":
                N = int(args.c)
            else:
                N = 10

            for c in cards:
                if c.ctype == mp.CID.comment:
                    ccc = c.card()
                    l = len(ccc.splitlines())
                    if l >= N:
                        print(c.pos, l)
                        print(ccc, end='')

        elif args.mode == 'extr':
            # extract cell specified in -c keyword and necessary materials, and
            # surfaces.
            cset = set()
            flag = ''  # can be '!'
            if args.c != '0':
                if '!' in args.c:
                    args.c = args.c.replace('!', ' ')
                    flag = '!'
                le = rin.expand(args.c.split())
                cset = set(le)
            if args.map != '':
                # cset = set()
                for l in open(args.map, 'r'):
                    for c in l.split():
                        cset.add(int(c))
            # get set of all cells:
            aset = set()
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.cell:
                    aset.add(c.name)

            extract_parents_flag = True
            if args.u != '0':
                if '_' in args.u:
                    extract_parents_flag = False
                    args.u = args.u.replace('_', ' ')
                else:
                    extract_parents_flag = True
                uref = int(args.u)
                for c in cards:
                    if c.ctype == mp.CID.cell:
                        u = c.get_u()
                        u = 0 if u is None else u
                        if u == uref:
                            cset.add(c.name)

            # '!' means that the specified cells should NOT be extracted, but
            # all other.
            if flag == '!':
                cset = aset.difference(cset)
            if not cset:
                print("No cells to extract are specified")
                raise Exception

            # first, get all surfaces needed to represent the cn cell.
            sset = set()  # surfaces
            mset = set()  # material
            tset = set()  # transformations
            uset = set()  # universes that fill cells of cset
            fset = set()  # universes that the cells of cset belong to.
            Uset = set()  # set of universes, parets belong to.
            pset = set()  # parent cells, ie. cells filled with u-s from fset.

            # first run through cards: define filling
            for c in cards:
                if c.ctype == mp.CID.cell:
                    if c.name in cset:
                        if extract_parents_flag and c.get_f() is not None:
                            uset.add(c.get_f())
                        if extract_parents_flag and c.get_u() is not None:
                            fset.add(c.get_u())

            # next runs: find all other cells:
            again = True
            while again:
                again = False
                for c in cards:
                    if c.ctype == mp.CID.cell:
                        if c.get_u() in uset:
                            cset.add(c.name)
                            if c.get_f() is not None:
                                if c.get_f() not in uset:
                                    uset.add(c.get_f())
                                    again = True
                        if c.name in cset:
                            cref = c.get_refcells()
                            if cref.difference(cset):
                                again = True
                                cset = cset.union(cref)
                        if c.get_f() in fset:
                            # this cell is parent of one of cset.
                            pset.add(c.name)
                            if c.get_u() not in Uset:
                                again = True
                                Uset.add(c.get_u())
                        if c.get_u() in Uset:
                            if c.get_f() not in fset:
                                c.get_f(newv=0)
                            pset.add(c.name)

            # final run: for all cells find surfaces, materials, etc.
            cset = cset.union(pset)
            for c in cards:
                if c.ctype == mp.CID.cell and c.name in cset:
                    # get all surface names and the material, if any.
                    for v, t in c.values:
                        if t == 'sur':
                            sset.add(v)
                        elif t == 'mat':
                            mset.add(v)
                        elif t == 'tr':
                            tset.add(v)

                if c.ctype == mp.CID.surface and c.name in sset:
                    # surface card can refer to tr
                    for v, t in c.values:
                        if t == 'tr':
                            tset.add(v)

            blk = None
            for c in cards:
                if c.ctype == mp.CID.title:
                    print(c.card(), end='')
                if c.ctype == mp.CID.cell and c.name in cset:
                    print(c.card(), end='')
                    blk = c.ctype
                if c.ctype == mp.CID.surface:
                    if blk == mp.CID.cell:
                        print()
                        blk = c.ctype
                    if c.name in sset:
                        print(c.card(), end='')
                if c.ctype == mp.CID.data:
                    if blk != c.ctype:
                        print()
                        blk = c.ctype
                    if c.dtype == 'Mn' and c.values[0][0] in mset:
                        print(c.card(), end='')
                    if c.dtype == 'TRn':  # and c.values[0][0] in tset:
                        print(c.card(), end='')

        elif args.mode == 'nogq':
            from numjuggler import nogq
            trn0 = int(args.t)
            cflag = False if args.c == "0" else True

            vfmt = ' {:15.8e}'*3
            tfmt = 'tr{} 0 0 0 ' + ('\n     ' + vfmt)*3
            trd = {}
            # replace GQ cylinders with c/x + tr
            for c in cards:
                crd = c.card()
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    if c.stype == 'gq':
                        p = nogq.get_gq_params(' '.join(c.input))
                        a2, g, kk = nogq.get_k(p)
                        if cflag:
                            crd = (crd[:-1] +
                                   '$ a^2={:12.6e} c={:12.6e}\n'.format(a2,
                                                                        g + a2))
                        if abs((g + a2) / a2) < 1e-6:
                            # this is a cylinder. Comment original card and
                            # write another one
                            R, x0, i, j = nogq.cylinder(p, a2, g, kk)
                            # add transformation set
                            tr = tuple(i) + tuple(j) + tuple(kk)
                            for k, v in list(trd.items()):
                                if tr == v:
                                    trn = k
                                    break
                            else:
                                trn = len(trd) + 1
                                trd[trn] = tr
                            # replace surface card
                            if cflag:
                                crd = ('c ' +
                                       '\nc '.join(c.card().splitlines()) +
                                       '\n')
                            else:
                                crd = ''
                            crd += '{} {} c/z {:15.8e} 0 {:15.8e}\n'.format(
                                c.name, trn + trn0, x0, R)
                            # crd += 'c a^2={:12.6e} g={:12.6e} k={}\n'.format(a2, g, kk)
                print(crd, end='')
                if trd and c.ctype == mp.CID.blankline:
                    # this is blankline after surfaces. Put tr cards here
                    for k, v in sorted(trd.items()):
                        ijk = (k + trn0,) + v
                        print(tfmt.format(*ijk))
                    trd = {}

        elif args.mode == 'nogq2':
            from numjuggler import nogq2
            trn0 = int(args.t)
            cflag = False if args.c == "0" else True

            vfmt = ' {:15.8e}'
            tfmt = 'tr{} 0 0 0  ' + ('\n     ' + 3*vfmt) * 3
            cfmt = '{} {}  {} ' + 3*vfmt + '\n'
            kfmt = '{} {}  {} ' + 3*vfmt + '\n      ' + vfmt + '\n'
            trd = {}
            trn = 0
            # replace GQ cylinders with c/x + tr
            for c in cards:
                crd = c.card()
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    if c.stype == 'gq':
                        tuf, pl = nogq2.get_params(' '.join(c.input))
                        typ, a, o, t2, r2, cl = nogq2.get_cone_or_cyl(pl)
                        print('c Log for GQ card {}'.format(c.name))
                        for comment in cl:
                            print(comment)
                        crd1 = crd.splitlines()
                        if typ in 'ck' and not tuf and trn + trn0 < 999:
                            bbb, aaa = nogq2.basis_on_axis(a)
                            # bbb is the basis, where the cylinder/cone axis is
                            # parallel to axis aaa. In this basis, the origin o
                            # of the cylinder/cone is:
                            oprime = nogq2.transform(o, bbb, (0, 0, 0))
                            # add transformation set
                            tr = sum(bbb, ())  # sum of 3 3-tuples is a 9-tuple
                            if aaa == 'x':
                                c1 = oprime[1]
                                c2 = oprime[2]
                            elif aaa == 'y':
                                c1 = oprime[0]
                                c2 = oprime[2]
                            else:
                                c1 = oprime[0]
                                c2 = oprime[1]
                            for k, v in trd.items():
                                for e1, e2 in zip(v, tr):
                                    if not nogq2.areclose((e1, e2), atol=1e-7, rtol=None):
                                        break
                                else:
                                    trn = k
                                    break
                            else:
                                trn = len(trd) + 1
                                trd[trn] = tr
                            # Comment the original surface card and add
                            # information about type, axis, origin and params
                            if cflag:
                                crd = multiline(crd1 + cl, 'c ') + '\n'
                            else:
                                crd = ''

                            if typ == 'c':
                                aaa = 'c/' + aaa
                                p = r2**0.5  # cylinder radius
                                crd += cfmt.format(c.name,
                                                   trn + trn0,
                                                   aaa,
                                                   c1, c2, p)
                            elif typ == 'k':
                                aaa = 'k/' + aaa
                                p = t2  # square tan of half-angle
                                c0, c1, c2 = oprime
                                crd += kfmt.format(c.name,
                                                   trn + trn0,
                                                   aaa,
                                                   c0, c1, c2, p)
                        elif tuf:
                            # GQ with transform, do not modify
                            crd = multiline(crd1) + '\n'
                        else:
                            # failed to convert GQ card. Use the original one
                            # and print additional information
                            crd = multiline(crd1 + cl) + '\n'

                print(crd, end='')
                if trd and c.ctype == mp.CID.blankline:
                    # this is blankline after surfaces. Put tr cards here
                    for k, v in sorted(trd.items()):
                        v = (0, 0, 0) + v
                        print(tr2str(v).format(k + trn0))
                        # ijk = (k + trn0,) + v
                        # print(tfmt.format(*ijk))
                    trd = {}

        elif args.mode == 'count':
            # take the maximal number of surfaces from -s:
            Nmax = int(args.s)
            if Nmax == 0:
                Nmax = 100  # default max value.
            print(('{:>10s}'*5).format('Cell',
                                       'Line',
                                       'all',
                                       'unique',
                                       '>{}'.format(Nmax)))
            sc = 0  # cell counter
            sa = 0  # all surfaces counter
            su = 0  # unique surface counter
            ma = 0  # maximal number of all surfaces
            mu = 0  # maximal number of unique surfaces
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    # get list of surfaces used in the cell:
                    los = []
                    for v, t in c.values:
                        if 'sur' in t:
                            los.append(v)

                    # output number of surfaces:
                    a = len(los)       # number of all surfaces
                    u = len(set(los))  # number of unique surfaces
                    print(('{:>10d}'*4).format(c.name, c.pos, a, u), end='')
                    if a > Nmax:
                        print(' *')
                    else:
                        print(' ')
                    sc += 1
                    sa += a
                    su += u
                    ma = max(ma, a)
                    mu = max(mu, u)
            print()
            print('sum', ('{:>10d}'*3).format(sc, sa, su))
            print('max', ('{:>10d}'*3).format(00, ma, mu))

        elif args.mode == 'nofill':
            # remove all fill= keywords from cell cards.

            # Get universes to withdraw from command line parameters
            uset = set(rin.expand(args.u.replace('!', ' ').split()))

            # If -u contains !, reverse uset
            if '!' in args.u:
                def check(v, s):
                    return v not in s
            else:
                def check(v, s):
                    return v in s

            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()

                    for v, t in c.values:
                        if t == 'fill':
                            if check(v, uset):
                                c.remove_fill()
                            break
                lines = '\n'.join(filter(lambda s: s.strip(),
                                         c.card().splitlines()))

                print(lines)


        elif args.mode == 'matinfo':
            # for each material used in cell cards, output list of cells
            # together with density and universe.
            res = {}
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    m = c.get_m()
                    d = c.get_d()
                    u = c.get_u()
                    l = res.get(m, [])
                    if not l:
                        res[m] = l
                    l.append((c.name, d, u))
                if c.ctype == mp.CID.surface:
                    break

            # print out information
            fmt = ' '*8 + '{:>16}'*3
            print(fmt.format('Cell', 'density', 'universe'))
            for m in sorted(res.keys()):
                uset = set()
                for c, d, u in res[m]:
                    uset.add(u)
                print('m{} -------------- {} {}'.format(m,
                                                        len(uset),
                                                        sorted(uset)))

                for c, d, u in res[m]:
                    print(fmt.format(c, d, u))

                # Get a compact list of cells for material m
                cells = list(e[0] for e in res[m])
                print('Compact list of cells for material m{}: '.format(m))
                print(' '.join(map(str, rin.shorten(cells))))



            # If -m option is given, try to get cell volumes from there
            # -m argument is the mctal name followed by tally number of the
            # tally containing cell volumes.
            if args.m != '0':
                assert Mctal is not None, "pirs Mctal class is not imported"
                mctal = Mctal()
                fname, tn = args.m.split()
                tn = int(tn)
                mctal.read_complete(fname)
                tv = mctal.mctaltallies[tn]
                cn = tv.fnl_numpy    # cell numbers
                cv = tv.vals_numpy   # cell volumes

                # Compute material weights
                res = {}   # values are tuples (volume, weight)
                for c in cards:
                    if c.ctype == mp.CID.cell:
                        if c.name in cn:
                            m = c.get_m()
                            d = c.get_d()
                            if m not in res:
                                res[m] = (0., 0.)
                            v = cv[0, cn == c.name][0]

                            res[m] = (res[m][0] + v, res[m][1] + v*d)
                        else:
                            print('No volume for cell ', c.name)
                    if c.ctype == mp.CID.surface:
                        break

                print(('{:>20s}'*3).format('Material', 'Volume', 'Weight'))
                sv = 0.0
                sw = 0.0
                for m, (v, w) in sorted(res.items()):
                    print('{:20d}{:20e}{:20e}'.format(m, v, w))
                    if m > 0:
                        sv += v
                        sw += w
                print('{:>20s}{:20e}{:20e}'.format('total nonvoid:', sv, sw))


        elif args.mode == 'uinfo':
            # for each universe return list of its cells.
            res = {}
            fd = {}  # dictionary of cells, filled with another universe

            # flag to sort cells in the output list:
            sflag = False if args.s == "0" else True
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    u = c.get_u()
                    f = c.get_f()
                    u = 0 if u is None else u
                    l = res.get(u, [])
                    if not l:
                        res[u] = l
                    l.append(c.name)
                elif c.ctype == mp.CID.surface:
                    break
            # print out
            if args.u == '0':
                for u, l in sorted(res.items()):
                    if sflag:
                        l = sorted(l)
                    print('u{} '.format(u), end='')
                    for e in rin.shorten(l):
                        print(e, end=' ')
                    print()
                    print(len(l))
            else:
                uref = int(args.u)
                l = res[uref]
                if sflag:
                    l = sorted(l)
                for e in rin.shorten(l):
                    print(e, end='')
            # print tabulated "tree", see E-mail of Marco Fabri, 8.11.2017
            for u, cl in sorted(res.items()):
                print('Cells in universe ', u)
                for c in cl:
                    print(c, fd.get(c, ''))



        elif args.mode == 'impinfo':

            if args.m == '0':
                for c in cards:
                    if c.ctype == mp.CID.cell:
                        c.get_values()
                        i = c.get_imp()
                        if 0 in list(i.values()):
                            print(c.card(), end='')
            else:
                nv = {}
                for t in args.m.split():
                    # form of args.m: "n1.0 p0 e0"
                    nv[t[0]] = float(t[1:])
                for c in cards:
                    if c.ctype == mp.CID.cell:
                        c.get_values()
                        c.get_imp(nv)
                    print(c.card(), end='')

        elif args.mode == 'sinfo':
            # first, get the list of surfaces:
            sl = {}
            st = set()  # set of used surface types
            for c in cards:
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    sl[c.name] = (set(), c.stype)
                    st.add(c.stype)
            # for each surface return list of cells:
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    for v, t in c.values:
                        if t == 'sur':
                            sl[v][0].add(c.name)
            # print out:
            for s, (cs, t) in sorted(sl.items()):
                print(s, t, sorted(cs))
            for s in sorted(st):
                print(s)

        elif args.mode == 'minfo':

            countfmt = """ Total words            :{d[0]:9}
 Total hash             :{d[1]:9}
 Hashcel                :{d[2]:9}
 Hashsurf               :{d[3]:9}"""

            cellfmt  = """ Longest cell           :{:9}
 Words in longest cell  :{:9}"""

            mcnpfmt  = """
 MCNP estimation :
     mlja                         :{:11}
     Estimated memory requirement :     {:5.1f}{}
     %cell length, %number #      :       {:4.1%}   {:4.1%}"""
            hashcellfmt = "   {:>9s}        {d[0]:3}      {d[1]:3}      {d[2]:3}"
            munits=['bytes','kB','MB','GB','TB']
            stat_tot  = [0,0,0,0]
            longest_c = None
            maxword   = 0
            ic = 0
            mlja = 0
            hashlist = []
            for c in cards:
               if c.ctype == mp.CID.cell:
                  ic += 1
                  cardstr = stc.cell_card_string(''.join(c.lines))
                  cs=cardstr.get_stat()
                  if ( ic > 50 and mlja > 3250) :
                      mlja += 7 * cs[0]
                  else:
                      mlja += 17 * cs[0]
                  if ( cs[0] > maxword ) :
                      c.get_values()
                      maxword   = cs[0]
                      longest_c = c.name
                  stat_tot=[a+b for a,b in zip(stat_tot,cs)]
                  if ( cs[1] > 0 ):
                      hashlist.append([cardstr.headstr.split()[0],cs[1:]])
            mljacell = mlja
            mlja = mlja + 2*17*maxword*stat_tot[1]
            mem  = mlja * 4 * 4.   # 4 times mlja, 4 bytes integer
            im = 0
            while mem > 1024 :
                im += 1
                mem = mem / 1024

            pcel = float(mljacell)/mlja
            phash = 1 - pcel
            print ( countfmt.format(d=stat_tot) )
            print ( cellfmt.format( longest_c, maxword ))
            print ( mcnpfmt.format( mlja, mem, munits[im], pcel, phash ))
            print ( '\n   Cell name    total #   cell #   surf #'  )
            for c in hashlist:
                print ( hashcellfmt.format(c[0],d=c[1]) )

        elif args.mode == 'vsource':

            def print_planar(params, d=1e-5, u='0'):

                # u defines which sdef is printed:
                if '_' in u:
                    v = -1
                    u = u.replace('_', '')
                elif '+' in u:
                    v = 1
                    u = u.replace('+', '')
                else:
                    v = 1

                c = ['c x', 'c y', 'c z']
                if u in 'xX':
                    c[0] = '  '
                elif u in 'yY':
                    c[1] = '  '
                elif u in 'zZ':
                    c[2] = '  '
                x1, x2, y1, y2, z1, z2 = params[:]
                dx = x2 - x1
                dy = y2 - y1
                dz = z2 - z1
                mx = (x1 + x2)*0.5
                my = (y1 + y2)*0.5
                mz = (z1 + z2)*0.5
                xs = mx - (dx*0.5 - d)*v
                ys = my - (dy*0.5 - d)*v
                zs = mz - (dz*0.5 - d)*v
                if u in 'xX':
                    fmt = 'sdef x {:12} y d2  z d3  vec {} dir 1 wgt {}'
                    print(fmt.format(xs, '{} 0 0'.format(v), dz*dy))
                elif u in 'yY':
                    fmt = 'sdef y {:12} x d1  z d3  vec {} dir 1 wgt {}'
                    print(fmt.format(ys, '0 {} 0'.format(v), dx*dz))
                elif u in 'zZ':
                    fmt = 'sdef z {:12} x d1  y d2  vec {} dir 1 wgt {}'
                    print(fmt.format(zs, '0 0 {}'.format(v), dx*dy))

                fm2 = 'si{:1} h {:12} {:12} $ {} {}'
                print(fm2.format(1, x1 + d, x2 - d, dx, mx))
                print(fm2.format(2, y1 + d, y2 - d, dy, my))
                print(fm2.format(3, z1 + d, z2 - d, dz, mz))
                fm3 = 'sp{:1} d 0 1'
                print(fm3.format(1))
                print(fm3.format(2))
                print(fm3.format(3))

            def print_spherical(s, r):
                """
                s -- spherical surface number, r -- its radius. Radius is
                needed to compute weight for volume calculations.
                """
                print('sdef sur {} nrm -1 wgt {:12.7e}'.format(s, Pi * r**2))

            # Set of surface names to be checked for surface source candidates
            sset = set()
            if args.s != '0':
                sset = set(rin.expand(args.s.split()))


            # Try to find proper surfaces:
            surfaces = dict(zip('xyzs', (None,)*4))
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                if c.ctype == mp.CID.surface:
                    c.get_values()
                    if not sset or c.name in sset:
                        if c.stype in ('px', 'py', 'pz', 'so', 's'):
                            # this is surface-candidate. Check its parameters:
                            k = c.stype.replace('p', '').replace('o', '')
                            if k == 'p':
                                v = c.scoefs[0]  # plane position
                            else:
                                v = c.scoefs[-1] # sphere radius
                            if surfaces[k] is None:
                                surfaces[k] = (c.name, v, c.name, v)
                            else:
                                n1, v1, n2, v2 = surfaces[k]
                                if v1 > v:
                                    surfaces[k] = (c.name, v, n2, v2)
                                if v2 < v:
                                    surfaces[k] = (n1, v1, c.name, v)
            print_sdef = True
            for k, v in surfaces.items():
                if v is not None:
                    n1, v1, n2, v2 = v
                    print('c ', k, n1, v1)
                    print('c ', k, n2, v2)
                elif k == 's' and args.u in 'sS':
                    # propose parameters of the circumscribing sphere
                    x = surfaces['x']
                    y = surfaces['y']
                    z = surfaces['z']
                    cx = (x[1] + x[3])*0.5
                    cy = (y[1] + y[3])*0.5
                    cz = (z[1] + z[3])*0.5
                    r = ((x[3] - x[1])**2 +
                         (y[3] - y[1])**2 +
                         (z[3] - z[1])**2)**(0.5) * 0.55

                    # Next free surface number:
                    d = mn.get_numbers(cards)
                    ns = max(d['sur']) + 1
                    nc = max(d['cel']) + 1
                    print('c universe with circumscribing sphere')
                    print('{} 0 {} imp:n=1 imp:p=1 u=1 '.format(nc, -ns))
                    print('{} 0  {} imp:n=0 imp:p=0 u=1 '.format(nc+1, ns))
                    print()
                    print('c Circumscribing sphere: ')
                    print(ns, k, cx, cy, cz, r)
                    surfaces[k] = (ns, r, ns, r)
                    print_sdef = False

            # Process -u key
            if args.u[-1] in 'xXyYzZ':
                # planar source
                params = []
                for k in 'xyz':
                    if surfaces[k] is None:
                        print(k)
                        raise ValueError('Planes not found for planar source')
                    else:
                        n1, v1, n2, v2 = surfaces[k]
                        params.extend([v1, v2])
                print_planar(params, d=1e-5, u=args.u)
            elif args.u == 's':
                if surfaces['s'] is None:
                    raise ValueError('Spheres not found for spherical source')
                else:
                    n1, v1, n2, v2 = surfaces['s']
                if print_sdef:
                    print_spherical(n2, v2)

            if args.c != '0':
                print('c source from -c parameters')
                vals = list(map(float, args.c.split()))
                if len(vals) == 6:
                    # x, y and z range of a box:
                    print_planar(vals, u=args.u)
                else:
                    raise ValueError('Wrong number of entries in the -c option')


        elif args.mode == 'fillempty':
            # add 'FILL =' to all void non-filled cells.
            # N = ' fill={} '.format(args.u)
            N = args.u
            M = int(args.m)
            cll = []  # list of cell lists to be filled with new u
            fl = []   # list of new u that fills cells from cll
            if args.map != '':
                # read from map list of cells where to insert the fill card
                for l in open(args.map):
                    if ':' in l:
                        # l contains cell numbers and its filling
                        s1, s2 = l.split(':')
                        cll.append(rin.expand(s1.split()))
                        fl.append(s2)
                    else:
                        cll.append(rin.expand(l.split()))
                        fl.append(N)
            if args.c != '0':
                cll.append(rin.expand(args.c.split()))
                fl.append(N)

            # put cll and fl into a single dict:
            dll = {}
            if cll:
                for cl, f in zip(cll, fl):
                    for c in cl:
                        dll[c] = f

            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    if dll:
                        if c.name in dll:
                            c.input[-1] += dll[c.name]
                    else:
                        m = c.get_m()
                        f = c.get_f()
                        imp = c.get_imp()
                        if imp['imp:n'] > 0 and m == M and f in [0, None]:
                            c.input[-1] += N
                print(c.card(), end='')

        elif args.mode == 'renum':
            if args.map:
                maps = lf.read_map_file(args.map, log=args.log != '')
            else:
                maps = {}

            for c in cards:
                c.get_values()

            # index dictionary only if needed:
            if 'i' in (args.c, args.s, args.m, args.u):
                imaps = lf.get_indices(cards, log=args.log != '')

            for t in ['cel', 'sur', 'mat', 'u', 'tr']:
                # If command line paramters are specified, they rewrite maps
                # from the map file
                dn = getattr(args, t[0])
                if dn == 'i':
                    maps[t] = imaps[t]
                    maps[t].doc = 'Indexing function for {}'.format(t)
                    maps[t].default = None   # This will raise error if applied to non-existent value
                elif dn != '0':
                    maps[t] = lf.LikeFunction(log=args.log != '')
                    maps[t].default = lf.add_func(int(dn))

                    # do not modify zero numbers (important for material
                    # numbers)
                    maps[t].mappings[lf.Range(0)] = lf.const_func(0)

                    maps[t].doc = 'Function for {} from command line'.format(t)


            for c in cards:
                c.apply_map(maps)
                print(c.card(), end='')

            if args.log != '':
                for k, m in maps.items():
                    m.write_log_as_map(k[0], args.log)


if __name__ == '__main__':
    main()
