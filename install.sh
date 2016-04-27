#!/bin/bash 

#
#
# Installs a link to current directory. 
# Thus, changes in any py files do not require
# reinstallation. 
#
# However, the numjuggler script is generated
# automatically and contains current version numger.
# If this number is chaged in setup.py, the
# package should be reinstalled, in order
# to update the numjuggler script.


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
pip install -e . 
# pip install dist/numjuggler*.tar.gz $user

