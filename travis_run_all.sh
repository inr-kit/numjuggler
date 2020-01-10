#!/bin/bash

# Assuming that numjuggler is installed properly 
# and tests are in travis_tests(see .travis.yml)

odir=$(pwd)

cd $odir/travis_tests/renum
i=i1
o="-c 10 -s 5 -m 100"
numjuggler $o $i.i > $i.res && diff -w $i.ref $i.res > $i.diff || exit 1

cd $odir/travis_tests/remh
i=nested_complement
o="--mode remh"
numjuggler $o $i.i > $i.res && diff -w $i.ref $i.res > $i.diff || exit 1

