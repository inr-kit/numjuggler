EXECUTION MODES
---------------

The ``--mode`` argument defines the execution mode of the script. It can have the
following string values:


renum:
    The default mode. Cells, surfaces, materials and universes are renamed
    according to the -c, -s, -m, -u or ``--map`` command line options. The original
    MCNP input file is not modified, the input file with renamed elements is
    written to standard output.


info:
    The input file is analysed and ranges of used numbers for cells, surfaces,
    ets. are written out. Note that the output of this mode can be used
    (after necessary modifications) as the input to the ``--map`` option.

    The first two columns specify type (cells, surfaces, etc.) and the range of
    used numbers. The third column shows the amount of numbers in current range,
    and the last column shows how many numbers left unused between the current
    and previous ranges.


wrap:
    Wrap lines in the MCNP input file to fit the 80-chars limit. Only
    the line meaningful parts are wrapped: if a line exceed 80 characters due to
    a comment (i.e. any entries after "$" or "&"), it is not wrapped.


rems:
    Replace multiple spaces with only one space. This operation is performed
    only to the meaningful parts of the input file, i.e. comments are leaved
    unchanged.


remc:
    remove all external comment lines (external means between cards).


minfo:
    Count the number of words, complementary operators and estimate the size of 
    MCNP lja vector


remh:
    Remove all (when possible) complementary operators. Complementary operators
    referring to transformed cell cannot be removed.


uexp:
    Add explicit "u=0" to cells with no "u" parameter. This can be useful when
    combining several input files into one model using universes. When cells
    have explicit zero universes, they can be renumbered using the -u or ``--map``
    option in subsequent runs.

    Another universe can be specified with the -u option. IN this case, the
    whole option should be specified, i.e. -u ' u=1 '

    The -c option can be used to specify cells to be handled. Examples:

         -c "1 --150" -- add universe option only to these cells.
         -c "!2" -- do not add universe to cell 2, even if it safisfies above
         criteria


split:
    Split input into several files containing separate blocks. Output is written
    to files

        inp.1message
        inp.2title
        inp.3cells
        inp.4surfaces
        inp.5data

    where inp is replaced by the name of the ofiginal input file. Note that
    separate blocks do not contain blank lines. In order to concatenate block
    files together into a single input, one needs to insert blank lines:

    > numjuggler --mode split inp_
    > cat inp_.[1-5]* > inp2_          # inp2_ lacks all blank lines
    > echo '' > bl
    > cat inp_.1* bl inp_.2* inp_.3* bl inp_.4* bl inp_.5* bl > inp3_

    After these commands, file `inp3_` is equivalent to `inp_`.


mdupl:
    remove duplicate material cards. If an input file contains several mateiral
    cards with the same name (number), only the first one is kept, the other
    are skipped.


matan:
    Compare all meterials and list possible duplicates.


sdupl:
    Report duplicate (close) surfaces.


msimp:
    Simplify material cards.


extr:
    Extract the cell specified in the -c keyword together with materials,
    surfaces and transformations.

    If the first entry of the -c keyword is `!`, extract all but the cells
    specified after.


nogq:
    Replaces GQ cards representing a cylinder with c/x plus tr card. In some
    cases this improves precision of cylinder's representations and helps to
    fix lost particle errors.

    Transformation card numbering starts from the number specified in -t
    argument.

    If -c is given and differs from "0", the original GQ cards remain in the
    input, but commented out.  Otherwise (i.e. by default), they disappear from
    the input.


count:
    Returns a list of cells with the number of surfaces used to define cell's
    geometry.  Two values returned for each cell: total amount of surfaces
    mentioned in the cell geometry, and the number of unique surfaces (that is
    equal or less than the former).

    Cells with total number of surfaces exceeding 100 (or the value given as
    `-s` command line parameter) are denoted in the output with `*`


nofill:
    Under counstruction: Removes all 'fill=' keywords from cell cards.


fillempty:
    Add to all void non-filled cells with importance > 0 ``FILL = N``, where N
    is specified in the ``-u`` argument. When a material name is given with the
    -m argument, cells filled with this material are filled with N, instead of
    void cells.

    When a file is given with the ``--map`` option, a list of cells is read from
    this file, and the "fill=" is added to these cells only, independent on
    cell's importance or material.

    UPD: the content of -u option is copied into the input file as is. For
    example, to specify transformation in-place: ``-u '*fill=1 (0 0 5)'``.


matinfo:
    Output information about how materials are used: for each material list of
    cells with density and universe.

    When -m option is given, it must be the mctal file with calculation of
    cell volumes, followed by the tally number (for a tally prepared with the
    ``--mode`` tallies). In this case,  additionaly a summary of material weights
    is printed out.

    Example: read tally 14 from file `inp_m` to compute material masses

    >numjuggler --mode matinfo -m "inp_m 14" inp_ > inp_.matinfo


uinfo:
    For each universe defined in the input file, return a list of cells in this
    universe.


impinfo:
    List all cells with zero importances.


sinfo:
    For each surface defined in the input file, return the list of cells where
    it is used.

    At the end list all used types of surfaces.


vsource:
    Output data cards describing source for computation of volumes. Model
    dimensions must be specified in the -c option as a rcc that circumscribes
    the model. For example,

    --mode vsource -c "10 20 -10 10 -20 20"

    will generate planar sources for the box 10 < x < 20, -10 < y < 10 and
    -20 < z < 20.

    --mode vsource -s 100

    will generate spherical source for the sphere 100.

    --mode vsource -s "10 11 12 13 14 15"

    will generate planar source based on parameters of planes 10 -- 15 (these
    surfaces must be px, py and pz planes).


tallies:
    Output tally cards for calculation of volumes in all cells. Tally number
    can be given with the -s option, and with non-zero -u one can specify cells
    of particular universe.


addgeom:
    appends strings, specified in ``--map`` file  to geometry definition of cells.
    Example of the map file:

    10  -1 , #12 #35
    11   1 , #12 #35
    135

    First entry -- cell, which geometry should be modified. Second entry till
    comma ('-1' and '1' in the above example) will be prepended to the cell's
    existing geometry definition, the rest after the comma will be appended
    after the existing geometry definition.

    If the cell number is not followed by any entry (including the comma), this
    cell will be removed from the resulting input file. In the above example,
    cell 135 will be removed.


merge:
    put two input files into a single file. Second input file is given in the -m
    option.


remu:
    Remove all cells that belong to the universe specified in the -u option, or
    cells specified in the -c option. Surfaces that are used only for the
    removed cells are removed as well.

    One can use the "I" MCNP short-hand notation in the -u and -c options to
    specify a range of universe or cell numbers.

    If the -u keyword string starts with "!", than all except the specified
    universes are removed.

    When universes to remove are given with the -u option, the FILL options are
    changed by replacing the removed universe numbers with the smallest universe
    number to be removed.

    One can specify additional cell cards and surface cards using the -m and -s
    options. The content of -m is appended to the card's block; the content of
    -s is prepended to the surface block.

    Examples:

        # Remove cells of universe 4

        > numjuggler --mode remu -u "4" inp.1 > inp.2


        # Remove cells of universes 4 and 5. In this case, FILL=5, if any, will
        # be replaced with FILL=4

        > numjuggler --mode remu -u "4 5" inp.1 > inp.2


        # Remove cells 1, 2 and 3:

        > numjuggler --mode remu -c "1 2 3" inp.1 > inp.2


        # Remove all universes except 4 and add description of cell 100 and
        # surface 100. All cells filled with deleted universes will be filled in
        # the new input file with cell 100:

        > numjuggler --mode remu -u "!4" \
                       -m "100 0 -100 imp:n=1 imp:p=1 u=4"\
                       -s "100 so 1e5"
                       inp.1 > inp.2


zrotate:
    rotate gometry around z-axis to the angle specified in -c parameter.
    Rotation is applied by defining the transformation card and applying it to
    surfaces without transformations. And all existing pure rotational
    transformations are changed.

    
annotate:
    Adds text from map file as multiline comment right after the title.


getc:
    Extract comments taking more than 10 (or given by -c option) lines.



