# General info 

Mapping rules can be specified in a separate file that is read when the `--map`
option is given.

Different from the `-c`, `-s`, `-m` and `-u` command line arguments, in the map
file one can specify mapping rules for separate ranges. Ultimately, all new
cell, surface, material or universe names can be given explicitly.


# map file format

A map file consists of lines of the following form:

    t [range]: [+-]D

The first entry, `t`, is the one-character type specification: `c` for cells,
`s` for surfaces, `m` for materials and `u` for universes.

It is optionally followed by the range specifier that can be a single number,
for example `10`, or two numbers delimited by two dashes, for example `10 --
25`. If the range is omitted, the line defines the default mapping, i.e. it is
applied to elements not belonging to all other ranges.

The semicolon, `:`, delimits the range specification from the specification of
the mapping rule.  It is followed by an integer, optionally signed. This
integer defines an increment to which numbers in the current range are
increased. The mapping in this case is `N -> N+D`, where `N` is the original
number from the range `[N1, N2]`.

When an unsigned integer is given together with the range specification, it is
considered as the first element of the mapped range. Mapping in this case is `N
-> N+D-N1`, where `N` in `[N1, N2]`.


# Map file examples

In the example below, cells from 1 to 10, inclusive, are renamed to the range
from 11 to 20, cell 200 is renamed to 250 and all other cells numbers are
incremented by 1000:

    c 1 -- 10: +10    # explicit sign means increment
    c 200:     250    # no sign means new number
    c:        1000    # all other cell numbers increment by 1000

Another example specifies that only universe number 0 should be modified:

    u 0: 10          # universe 0 will become number 10
    u: 0             # not necessary, while the trivial mapping is by default.


Provide all cell numbers explicitly, assuming that the input file has cells from 1 to
5 only:

    c 1: 12
    c 2: 14
    c 3: 16
    c 4: 18
    c 5: 20

Note that the [info](info.md) execution mode returns a list of all used ranges
and can be used as a template for the mapping file.

Only lines beginning with `c`, `s`, `u` or `m` and having the semicolon `:` are
taken into account; all other lines are ignored. After the semicolon, only one
entry is taken into account.


