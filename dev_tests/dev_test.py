"""
Test module in ./numjuggler without installing it.
"""

import sys
sys.path.insert(0, '..')

import numjuggler
print numjuggler.__file__

# test Range
from numjuggler.numbering import Range
print Range(1, 5)
print Range(1)
print Range(5, 1)
print 5 in Range(1, 3), 5 in Range(5)
print Range(), Range() == (0, -1)


# test reading of map file
import numjuggler.numbering
d1, d2 = numjuggler.numbering.read_map_file('map_file.txt')
print d1
print d2
