# numjuggler
Tool to rename cells, surfaces, materials and universes in MCNP input files.

## Install

You must have Python 2.7 installed on your machine (Python 3 was not tested but
might work). Unzip the  most recent archive from `dist` folder and run

    > python setup.py install --user

from the folder containing file `setup.py`. This installs the package, that can
be used from the command line in the following way:

    > python -m numjuggler ...

where ... -- are command line options specifying the input file and the rules
how cells, surfaces, etc. are renamed.

Alternatively, you can use [pip](https://pip.pypa.io/en/stable/) -- a tool for installing Python packages
(for some Python distributions it is included, otherwise must be installed separately). Unzipping the
archive in this case is not needed, and installation is done with the command

    > pip install numjuggler-X.X.X.tar.gz --user

When the package is installed with pip, a script called `numjuggler` is added to
`~/.local/bin` (or to `C:\Python27\Scripts`), so that invocation of the tool is
more simple. In this case, both two commands are identical:

    > numjuggler ...
    > python -m numjuggler ...

where .. -- are command line options.

## Help

After installing the package, run the following command to get some help and
instructions:

    > python -m numjuggler -h

There is also a repository on github, related to numjuggler documentation: https://github.com/inr-kit/numjuggler.docs . 

