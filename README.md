# WARNING
The versions starting with 2.23a.17 should be considered as untested. Since
version 2.22a.17, there were a lot of modifications toward more functionality,
however, these changes were applied only to a small set of problems and
therefore should be considered as not tested. If you experience any problems,
consider fall back to the version 2.22a.17.

Information in the help message, returned by ``numjuggler -h mode`` is
outdated. Therefore, the best way to see all current modes is to search for
``args.mode == `` string in ``main.py``, and read comments in the correspondent
sections of code.



# numjuggler
Tool to rename cells, surfaces, materials and universes in MCNP input files. See https://numjuggler.readthedocs.io

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

There is also a github repo, [numjuggler.docs](https://github.com/inr-kit/numjuggler.docs), related to numjuggler documentation.

