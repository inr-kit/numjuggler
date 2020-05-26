#!/bin/bash

# Will tab be printed as tab?
echo -e -"\t"- > itab.out
python -c 'print "=\t="' >> itab.out

# --preservetabs flag. The --debug flag turns off the use of dump file (which can also affect the tabs. BTW why?
numjuggler -s 10 itab_ --debug                > itab_.tabsno
numjuggler -s 10 itab_ --debug --preservetabs > itab_.tabsyes

