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
    option in subsequent runs.  """

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
    p.add_argument('--mode', type=str, help='Execution mode, "renum" by default', choices=['renum', 'info', 'wrap', 'uexp', 'rems'], default='renum')
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

