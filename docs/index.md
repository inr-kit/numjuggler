# numjuggler documentation

Github repo: [travleev/numjuggler](https://github.com/travleev/numjuggler)

The source for this documentation is located in the
[docs](https://github.com/travleev/numjuggler/tree/docs) branch. The
documentation is continually edited and updated: to get informed about updates
consider to [turn on
notifications](https://github.com/travleev/numjuggler/subscription). If you
miss some information, feel free to [open an
issue](https://github.com/travleev/numjuggler/issues/new).  Note: you need a
github account. 

[TOC]

## About 

Numjuggler is a command line tool to perform specific tasks on the MCNP input
files. 

Originally, it was developed at [INR-KIT](https://www.inr.kit.edu) to rename
cells, surfaces and materials in the MCNP input file. This task appeared
often within the framework of ITER nuclear analyses, where different parts of
the MCNP computational model were developed independently by different
organizations and than merged together to the model describing the whole ITER
facility. The merging of the model parts into a single MCNP input file was
often complicated by the use of the same cell, surface and material numbers
in the different model parts. 

Later, other features was added to numjuggler. Now it can be run in one of
the execution modes, each performing particular task. 

The original development was previously conducted in the [inr-kit
repository](https://github.com/inr-kit/numjuggler). The author of numjuggler
has its own fork at [travleev/numjuggler](https://travleev/numjuggler). 


## Installation 
TODO: the best way -- clone from travleev/numjuggler and install in the
"development mode" using pip: `pip install -e .`. 

TODO: try under windows/anaconda(?)

## Invocation

numjuggler is a command line tool written in Python. When properly installed,
it can be invoked in one of the following ways:

    >numjuggler           --mode <modename> [arguments] input.txt > input.new
    >python -m numjuggler --mode <modename> [arguments] input.txt > input.new
    
These two invocation forms are equal. The command line arguments in general
contain the only necessary argument -- the original MCNP input file (in the
above example `input.txt`). The output is written to standard output that can
be redirected to a file. The execution mode is specified after the  `--mode`
flag. The other optional arguments can define additional parameters relevant
to the chosen mode. 

TODO: how to get interactive help. 


## List of execution modes

In alphabetical order (links allude to existence of detailed information):

* addgeom
* annotate
* [cdens](cdens.md) -- change cell density
* combinec
* count
* extr
* fillempty
* getc
* impinfo
* [info](info.md) -- get input file statistics
* matan
* matinfo
* mdupl
* merge
* minfo
* mnew
* msimp
* nofill
* nogq
* nogq2
* remc
* remh
* remrp
* rems
* remu
* [renum](renum.md) -- renumber cells etc.
* sdupl
* sinfo
* split
* tallies
* uexp
* uinfo
* vsource
* wrap
* zrotate

Some information about the execution modes can be found in the source code, see
[main.py](https://github.com/travleev/numjuggler/blob/master/numjuggler/main.py).



## Limitations

Cell parameters (importance, universe) can be read only from the cell cards
block. Cell parameters specified in the data cards block are ignored.

Only subset of data cards is parsed to find cell, surface, etc. numbers. For
example, cell and surface numbers will be recognized in a tally card, but
material numbers will not be found in tally multiplier card. Also, cell and
surface numbers in the source-related cards are nor recognized.

Only a subset of execution modes were tested on the C-lite and C-model input
files. Current implementation is rather ineffective: complete renumbering of
cells and surfaces in C-lite takes 5 -- 10 min.

## Roadmap

* Organize automatic check of each new version: 
  
    * Write set of input files to be processed with different modes together with correspondent 
      resulting files
    * Connect to Travis CI (or similar) to perform automatic tests after each new commit to the master branch
    * Add icons passed/failed to documentation and the repo's README
    * Optional: formulate rules how to add new examples/test input files. 

* Clear interface to the interactive help (the ``--help`` command line argument with options) that takes information from docs folder, i.e.
  originates from the same source as the online web documentation.
  
