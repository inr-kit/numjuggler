#!/usr/bin/env python

import argparse as ap
import os.path
from numjuggler import numbering as mn
from numjuggler import parser as mp


# help messages already wrapped:
help_c = """
Cell number increment. If an integer is given, it is added to all cell numbers
(negative entries are valid as well). If "i" is given, cell numbers are
replaced by their sequence numbers, in the order as they appear in the input
file (the 1-st cell becomes number 1, etc)
"""[1:]  # here I remove the 1-st newline

help_s = '{} number increment, similar to "-c"'

dhelp = {}
dhelp['mode'] = """
EXECUTION MODES
---------------

The "--mode" argument defines the execution mode of the script. It can have the
following string values:


renum:
    The default mode. Cells, surfaces, materials and universes are renamed
    according to the -c, -s, -m, -u or --map command line options. The original
    MCNP input file is not modified, the input file with renamed elements in
    written to std.out.


info:
    The input file is analysed and ranges of used numbers for cells, surfaces,
    ets. is written to std.out. Note that output of this mode can be used
    (after necessary modifications) as input to the --map option.

    The first two columns specify type (cells, surfaces, etc.) and the range of
    used numbers. The third column shows the amount of numbers in current range,
    and the last column shows how many numbers left unused between the current
    and previous ranges.


wrap:
    Wrap lines in the MCNP input file to fit the 80-chars limit. Wrapped only
    meaningful parts of the lines: if a line exceed 80 characters due to
    comments (i.e.  any entries after "$" or "&"), it is not wrapped.


rems:
    Replace multiple spaces with only one space. This operation is performed
    only to the meaningful parts of the input file, i.e. comments are leaved
    unchanged.


uexp:
    Add explicit "u=0" to cells with no "u" parameter. This can be useful when
    combining several input files into one model using universes. When cells
    have explicit zero universes, they can be renumbered using the -u or --map
    option in subsequent runs.  

split: 
    Split input into several files containing separate blocks. Output is written
    to files

        inp.1message
        inp.2title
        inp.3cells
        inp.4surfaces
        inp.5data

    where inp is replaced by the name of the ofiginal input file. Note that
    separate blocks do not contain blank lines. In order to concatenate block files 
    together into a single input, one needs to insert blank lines:

    > numjuggler --mode split inp_
    > cat inp_.[1-5]* > inp2_          # inp2_ lacks all blank lines
    > echo '' > bl
    > cat inp_.1* bl inp_.2* bl inp_.3* bl inp_.4* bl inp_.5* bl > inp3_ # inp3_ is equivalent to inp_


mdupl:
    remove duplicate material cards. If an input file contains several mateiral
    cards with the same name (number), only the first one is kept, the other
    are skipped. 


sdupl:
    Report duplicate (close) surfaces.


msimp:
    Simplify material cards.
    
    
extr:
    Extract the cell specified in the -c keyword together with materials, surfaces 
    and transformations.
    
    
nogq:
    Replaces GQ cards representing a cylinder with c/x plus tr card. In some
    cases this improves precision of cylinder's representations and helps to
    fix lost particle errors.
    
    
count:
    Returns a list of cells with the number of surfaces used to define cell's
    geometry.  Two values returned for each cell: total amount of surfaces
    mentioned in the cell geometry, and the number of unique surfaces (that is
    equal or less than the former). 
    
    Cells with total number of surfaces exceeding 100 (or the value given as 
    `-s` command line parameter) are denoted in the output with `*`
    
    
nofill:
    Under counstruction: Removes all 'fill=' keywords from cell cards."""


dhelp['map'] = """
MAP FILE GENERAL INFO
---------------------

Mapping rules can be specified in a separate file that is read when --map
option is given.

Different from the -c, -s, -m and -u options, in the map file one can specify
mapping rules for separate ranges. Ultimately, all new cell, surface, material
or universe names can be given explicitly.


MAP FILE FORMAT
---------------

The map file consists of lines of the following form:

    t [range]: [+-]D

The first entry, t, is a one character type specification: "c" for cells, "s"
for surfaces, "m" for materials and "u" for universes.

It is optionally followed by the range specifier that can be one number, for
example "10", or two numbers delimited by two dashes, for example "10 -- 25". If
the range is omitted, the line defines the default mapping, i.e. it is applied
to elements not entering to all other ranges.

The semicolon, ":", delimits the range specification from the specification of
the mapping rule.  It is followed by an integer, optionally signed. This
integer defines an increment to which numbers in the current range are
increased. The mapping is than N -> N+D, where N is the original number from the
range [N1, N2].

When unsigned integer "D" is given on the line with range specification, i.e.
with "N1" or "N1 -- N2", it is considered as the first element of the mapped
range. Mapping in this case is N -> N+D-N1, where N in [N1, N2].


MAP FILE EXAMPLES
-----------------

In the example below, cells from 1 to 10 inclusive are renamed to the range from
11 to 20, cell 200 is renamed to 250 and to all other cells numbers are
incremented by 1000:

    c 1 -- 10: +10    # explicit sign means increment
    c 200:     250    # no sign means new number
    c:        1000    # all other cell numbers increment by 1000

Another example specifies that only universe number 0 should be modified:

    u 0: 10          # universe 0 will become number 10
    u: 0             # not necessary, while the trivial mapping is by default.


Provide all cell numbers explicitly (assume that input file has cells from 1 to
5):

    c 1: 12
    c 2: 14
    c 3: 16
    c 4: 18
    c 5: 20

Note that the --mode info option gives a list of all used ranges and can be used
as a basis for the mapping file.

Only lines beginning with "c", "s", "u" or "m" and having the semicolon ":" are
taken into account; all other lines are ignored. After the semicolon, only one
entry is taken into account.

"""

dhelp['examples'] = """
INVOCATION EXAMPLES
-------------------

Get extended help:

  > mcnp.juggler -h mode
  > mcnp.juggler -h map


Prepare model for insertion into another as universe 10:

  > mcnp.juggler --mode uexp inp > inp1     # add u=0 to real-world cells
  > echo "u0: 10 " > map.txt                # generate mapping file
  > mcnp.juggler --map map.txt inp1 > inp2  # replace u=0 with u=10
  > mcnp.juggler --mode wrap inp2 > inp3    # ensure all lines shorter 80 chars.


Rename all cells and surfaces by adding 1000:

  > mcnp.juggler -s 1000 -c 1000 inp > inp1
  > mcnp.juggler --mode wrap inp1 > inp2    # ensure all lines shorter 80 chars.


Rename all cells and surfaces by incrementing numbers as they appear in the
input file. To check renumbering, store log and use it on the next step as the
map file to perform the reverse renumbering.  Finally, remove extra spaces from
the resulting file and original one, in order to simplify visual comparison:

  > mcnp.juggler -c i -s i --log i1.log i1 > i2
  > mcnp.juggler --map i1.log i2 > i3       # apply log as map file for reverse renubmering
  > mcnp.juggler --mode rems i1 > c1        # remove extra spaces from original input
  > mcnp.juggler --mode rems i3 > c3        # and from result of reverse renumbering
  > vimdiff c1 c3                           # compare files visually


"""

dhelp['limitations'] = """
LIMITATIONS
-----------

Cell parameters can be read only from the cell cards block. Cell parameters
specified in the data cards block are ignored.

Only subset of data cards is parsed to find cell, surface, etc. numbers. For
example, cell and surface numbers will be recognized in a tally card, but
material numbers will not be found in tally multiplier card. Also, cell and
surface numbers in the source-related cards are nor recognized.

Only a subset of execution modes were tested on the C-lite model. Current
implementation is rather ineffective: complete renumbering of cells and
surfaces in C-lite takes 5 -- 10 min.


"""

descr = """
Renumber cells, surfaces, materials and universes in MCNP input file. The
original MCNP input file name must be given as command line option, the modified
MCNP input file is written to std.out." """[1:]

# dhelp keys as a string, with the last ',' replaced with 'or' for more humanity
dhelp_keys = str(dhelp.keys())[1:-1][::-1].replace(',', ' ro ', 1)[::-1]

epilog = """
Specify {} after -h for additional help.
"""[1:].format(dhelp_keys)


def main():
    p = ap.ArgumentParser(prog='numjuggler', description=descr, epilog=epilog) # formatter_class=ap.RawTextHelpFormatter)
    p.add_argument('inp', help='MCNP input file')
    p.add_argument('-c', help=help_c, type=str, default='0')
    p.add_argument('-s', help=help_s.format('Surface'), type=str, default='0')
    p.add_argument('-m', help=help_s.format('Material'), type=str, default='0')
    p.add_argument('-u', help=help_s.format('Universe'), type=str, default='0')
    p.add_argument('--map', type=str, help='File, containing descrption of mapping. When specified, options "-c", "-s", "-m" and "-u" are ignored.', default='')
    p.add_argument('--mode', type=str, help='Execution mode, "renum" by default', choices=['renum', 'info', 'wrap', 'uexp', 'rems', 'split', 'mdupl', 'sdupl', 'msimp', 'extr', 'nogq', 'count', 'nofill'], default='renum')
    p.add_argument('--debug', help='Additional output for debugging', action='store_true')
    p.add_argument('--log', type=str, help='Log file.', default='')

    # parse help option in another parser:
    ph = ap.ArgumentParser(add_help=False)
    ph.add_argument('-h', help='Print help and exit', nargs='?', default='', const='gen')
    harg, clo = ph.parse_known_args()
    if harg.h:
        if harg.h == 'gen':
            p.print_help()
        elif harg.h in dhelp.keys():
            print dhelp[harg.h]
        else:
            print 'No help for ', harg.h
            print 'Available help options: ', dhelp_keys
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
            print >> debuglog, 'command line arguments:', args
        else:
            debuglog = None

        # process input file only once:
        cards = list(mp.get_cards(args.inp, debuglog))

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
                if t[0] <> '#': # for meaning of '#' see parser.
                    nset = set(d.get(t, []))
                    print '-'* 40, t, len(nset)
                    rp = None
                    for r1, r2 in mn._get_ranges_from_set(nset):
                        print '{}{:>3s}'.format(indent, t[0]),
                        if r1 == r2:
                            rs = ' {}'.format(r1)
                        else:
                            rs = ' {} -- {}'.format(r1, r2)
                        if rp != None:
                            fr = '{}'.format(r1 - rp - 1)
                        else:
                            fr = ''
                        ur = '{}'.format(r2 - r1 + 1)
                        print '{:<30s} {:>8s} {:>8s}'.format(rs, ur, fr)
                        rp = r2
        elif args.mode == 'uexp':
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()
                    if 'u' not in map(lambda t: t[1], c.values):
                        c.input[-1] += ' u=0'
                print c.card(),

        elif args.mode == 'wrap':
            for c in cards:
                print c.card(True),

        elif args.mode == 'rems':
            for c in cards:
                c.remove_spaces()
                print c.card(),

        elif args.mode == 'split':
            # split input file into blocks
            fp = {}
            fp[mp.CID.message] = open(args.inp + '.1message', 'w')
            fp[mp.CID.title]   = open(args.inp + '.2title', 'w')
            fp[mp.CID.cell]    = open(args.inp + '.3cells', 'w')
            fp[mp.CID.surface] = open(args.inp + '.4surfaces', 'w')
            fp[mp.CID.data]    = open(args.inp + '.5data', 'w')
            cct = cards[0].ctype
            cmnt = None
            for c in cards:
                # blank line is attached to the end of block.
                # Comment is printed before the next card.
                if c.ctype > 0:
                    # where to print is defined by card ctype:
                    fff = fp[c.ctype]
                if c.ctype == mp.CID.comment:
                    # remember comment to print before next meaningful card
                    cmnt = c
                else:
                    if cmnt:
                        print >> fff, cmnt.card(),
                        cmnt = None
                    if c.ctype != mp.CID.blankline:
                        # do not print blank lines
                        print >> fff, c.card(),
            # do not forget the last comment
            if cmnt:
                print >> fff, cmnt.card(),


            for fff in fp.values():
                fff.close()

        elif args.mode == 'mdupl':
            # remove duplicate material cards, if they are equal.

            mset = set()
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.data and c.dtype == 'Mn':
                    if c.values[0][0] not in mset:
                        print c.card(),
                        mset.add(c.values[0][0])
                else:
                    print c.card(),

        elif args.mode == 'sdupl':
            # report duplicate (close) surfaces.
            # dict of unique surafces
            us = {}

            #  surface types coefficients that can only be proportional
            pcl =  {
                    'p': (0,),
                    'sq': (0, 7),
                    'gq': (0,)
                    }
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.surface:
                    # compare this surface with all previous and if unique, add to dict
                    print '--surface', c.card(),
                    ust = us.get(c.stype, {})
                    if ust == {}:
                        us[c.stype] = ust
                    for sn, s in ust.items():
                        if s.stype == c.stype:
                            # current surface card and s have the same type. Compare coefficients:
                            if mp.are_close_lists(s.scoefs, c.scoefs, pci=pcl.get(c.stype, [])):
                                print 'is close to {}'.format(sn)
                                break
                    else:
                        # add c to us:
                        cn = c.values[0][0]  # surface name
                        ust[cn] = c
                        print 'is unique'

        elif args.mode == 'msimp':
            # simplify material cards
            for c in cards:
                if c.ctype == mp.CID.data:
                    c.get_values()
                    if c.dtype == 'Mn':
                        inp = []
                        inp.append(c.input[0].replace('} ', '} 1001 1.0 $ msimpl ', 1))
                        for i in c.input[1:]:
                            inp.append('c msimpl ' + i)
                        c.input = inp
                print c.card(),

        elif args.mode == 'extr':
            # extract cell specified in -c keyword and necessary materials, and surfaces.
            cset = set(map(int, args.c.split()))
            # first, get all surfaces needed to represent the cn cell.
            sset = set() # surfaces
            mset = set() # material
            tset = set() # transformations
            uset = set() # universe

            # first run through cards: define filling
            for c in cards:
                c.get_values()
                if c.ctype == mp.CID.cell and c.name in cset:
                    if c.get_f() is not None:
                        uset.add(c.get_f())

            # next runs: find all other cells:
            for c in cards:
                if c.ctype == mp.CID.cell and c.get_u() in uset:
                    cset.add(c.name)

            # final run: for all cells find surfaces, materials, etc.                    
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
                    print c.card(),
                if c.ctype == mp.CID.cell and c.name in cset:
                    print c.card(),
                    blk = c.ctype
                if c.ctype == mp.CID.surface:
                    if blk == mp.CID.cell:
                        print
                        blk = c.ctype
                    if  c.name in sset:
                        print c.card(),
                if c.ctype == mp.CID.data :
                    if blk != c.ctype:
                        print
                        blk = c.ctype
                    if c.dtype == 'Mn' and c.values[0][0] in mset:
                        print c.card(),
                    if c.dtype == 'TRn' and c.values[0][0] in tset:
                        print c.card(),
        
        elif args.mode == 'nogq':
            from numjuggler import nogq
            try:
                # try because nogq requires numpy.
                from numjuggler import nogq
            except ImportError:
                print "Numpy package is required for --mode nogq but cannot be found. Install it with "
                print ""
                print " > pip install numpy"
                raise
            except:
                raise

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
                        a2, g, k = nogq.get_k(p)
                        crd = crd[:-1] + '$ a^2={:12.6e} c={:12.6e}\n'.format(a2, g + a2)
                        if abs((g + a2) / a2) < 1e-6:
                            # this is a cylinder. Comment original card and write another one
                            R, x0, i, j = nogq.cylinder(p, a2, g, k)                            
                            # add transformation set
                            tr = tuple(i) + tuple(j) + tuple(k) 
                            for k, v in trd.items():
                                if tr == v:
                                    trn = k
                                    break
                            else:
                                trn = len(trd) + 1
                                trd[trn] = tr
                            # replace surface card
                            crd = 'c ' + '\nc '.join(c.card().splitlines())
                            crd += '\n{} {} c/z {:15.8e} 0 {:15.8e}\n'.format(c.name, trn, x0, R)
                print crd,
                if trd and c.ctype == mp.CID.blankline:
                    # this is blankline after surfaces. Put tr cards here
                    for k, v in sorted(trd.items()):
                        ijk = (k,) + v 
                        print tfmt.format(*ijk)
                    trd = {}

        elif args.mode == 'count':
            # take the maximal number of surfaces from -s:
            Nmax = int(args.s) 
            if Nmax == 0:
                Nmax = 100 # default max value.
            print ('{:>10s}'*5).format('Cell', 'Line', 'all', 'unique', '>{}'.format(Nmax))
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
                    print ('{:>10d}'*4).format(c.name, c.pos, a, u),
                    if a > Nmax:
                        print ' *'
                    else:
                        print ' '

        elif args.mode == 'nofill':
            # remove all fill= keywords from cell cards. 
            print ' Mode --mode nofill is not implemented yet.'

            # First loop: find and remove all FILL keywords. Store universes for the second loop.
            uset = set()
            for c in cards:
                if c.ctype == mp.CID.cell:
                    c.get_values()

                    for v, t in c.values:
                        if t == 'fill':
                            uset.add(v)
                            c.remove_fill()
                            break
                print c.card(), 

            print 'Universes used for FILL:', uset





        elif args.mode == 'renum':
            for c in cards:
                c.get_values()

            if args.map:
                # if map file is given, ignore all -c, -s, -u and -m.
                dm = mn.read_map_file(args.map)

            else:
                # number: index dictionary only if needed:
                if 'i' in (args.c, args.s, args.m, args.u):
                    di = mn.get_indices(cards)
                else:
                    di = {}


                dm = {}
                for t in ['cel', 'sur', 'mat', 'u']:
                    dn = getattr(args, t[0])
                    if dn == 'i':
                        dm[t] = [None, di[t]] # None to raise an error, when None will be added to an int. (Indexes should be defined to all numbers, thus the default mapping should not be used.
                    else:
                        dm[t] = [int(dn), [(0, 0, 0)]] # do not modify zero material

            mapping = mn.LikeFunction(dm, args.log!='')

            for c in cards:
                c.apply_map(mapping)
                print c.card(),

            if args.log != '':
                mapping.write_log_as_map(args.log)


if __name__ == '__main__':
    main()

