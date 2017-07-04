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




