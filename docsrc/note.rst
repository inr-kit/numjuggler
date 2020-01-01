Organisation of documentation
==================================

Approach: put the source of documentation in md, and get text messages for
interactive help by converting md to txt. The md can be directly published with
the help of gh-pages.  Usage statistics can be collected with e.g. google
analytics. 

Task: Organize minimal structure with md files that can be used for publishing
and where information is read for interactive help. 


How the command line arguments of numjugller should look like?
=====================================================================================================

I want that each mode has its own set of command line options. General help
should provide the general form of the command line args. And there should be
a way to get particular info about each execution mode. For example::

   >numjuggler
   >numjuggler -h
   >numjuggler --help

   # General info, 
   # general commad line form,
   # the list of available modes,
   # how to get additional info


   >numjuggler -h <mode> 
   >numjuggler -h <mode> -i

   # Synopsis of the <mode>: short description and the list of available 
   # command line options. How to get additional info.


   >numjuggler -h <mode> -e
   # Examples for <mode>. 


   >numjuggler -h <mode> -a
   # Detailed description of the arguments

   >numjuggler -h <mode> -iea
   # Complete information about <mode>. The order of information does not
   # depend on the order of command line options, only itspresence. 

Usual invocation of numjuggler assumes particular execution mode. Previously,
there was the default mode, assumed if no ``--mode`` was given. This behaviour
should be preserved and one should understand how to distinguish between
the actual execution and asking for help. In the above examples, the command
line arguments always start with the ``-h`` or ``--help`` flag. 

