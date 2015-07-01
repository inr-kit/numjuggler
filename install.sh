#!/bin/bash 

#
#
# This script assumes pip.
#
#

# Uninstall previous version
pip uninstall numjuggler;

# prepare new distribution files 
python setup.py clean
rm dist/*
python setup.py sdist

# if in virtualenv, do not use the --user option:
if [ -z $VIRTUAL_ENV ]; then
    user="--user"
else
    user=""
fi;
pip install dist/numjuggler*.tar.gz $user

