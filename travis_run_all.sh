#!/bin/bash

# Assuming that numjuggler is installed properly 
# and tests are in travis_tests(see .travis.yml)

# Check numjuggler version 
numjuggler --version

odir=$(pwd)

cd $odir/travis_tests/renum
i=i1
o="-c 10 -s 5 -m 100"
numjuggler $o $i.i > $i.res && diff -w $i.ref $i.res > $i.diff || exit 1

cd $odir/travis_tests/remh
i=nested_complement
o="--mode remh"
numjuggler $o $i.i > $i.res && diff -w $i.ref $i.res > $i.diff || exit 1

cd $odir/travis_tests/cdens
i=inp.i
o="--mode cdens"
for m in $(ls map?); do
    echo $m
    numjuggler $o --map $m inp.i > inp.$m && diff -w inp.$m.ref inp.$m > $m.diff || exit 1
done
