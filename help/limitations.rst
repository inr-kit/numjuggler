LIMITATIONS
-----------

Cell parameters (importance, universe) can be read only from the cell cards
block. Cell parameters specified in the data cards block are ignored.

Only subset of data cards is parsed to find cell, surface, etc. numbers. For
example, cell and surface numbers will be recognized in a tally card, but
material numbers will not be found in tally multiplier card. Also, cell and
surface numbers in the source-related cards are nor recognized.

Only a subset of execution modes were tested on the C-lite and C-model input
files. Current implementation is rather ineffective: complete renumbering of
cells and surfaces in C-lite takes 5 -- 10 min.
