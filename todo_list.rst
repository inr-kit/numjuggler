Union cells
=============



When several input files merged into a single model, at least the "other world"
cells must be modified.

One can combine all "other worlds" of the original models into a single cell by
placing geometry description of the original "other world" cells into
parentheses and intersecting all of them.

Assume these are the original other-world cells of the separate models::

    100 0   AAA imp:n=0
    ...
    200 0   BBB imp:n=0

The other-world cells in the merged model is::

    300 0  (AAA) (BBB) imp:n=0

Possible UI::

    numjuggler --union -c "100 200 300" orig.inp > mod.inp

here we specify only cell number to be combined. The first non-existing cell
number defines the combined cell name. If all cell numbers exist, the combined
cell geometry is written to the 1-st cell mentioned in -c.


UPD:
--------
Implemented. Only existing cells are allowed in -c.


Generate file with plot commands
===================================


Modified syntax in the map file
====================================
For specification of range use MCNP I-notatation. Add possibility to specify range that does not changed by the default mapping.

UPD:
------

In the current inmplementation, I still use ``--``, which is simpler than the MCNP I-notation (no need to specify number of
inserted elements). Now one can mix separate values and ranges on the same line.

