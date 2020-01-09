#!/bin/bash

# Assuming that numjuggler is installed properly 
# and tests are in travis_tests(see .travis.yml)
cd travis_tests

numjuggler -c 10 -s 5 -m 100 i1 > i1.res && diff -w i1.ref i1.res > i1.diff || exit 1

