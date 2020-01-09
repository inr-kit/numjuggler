INVOCATION EXAMPLES
-------------------

Get extended help::

  > numjuggler -h mode
  > numjuggler -h map


Prepare model for insertion into another as universe 10::

  > numjuggler --mode uexp inp > inp1     # add u=0 to real-world cells
  > echo "u0: 10 " > map.txt                # generate mapping file
  > numjuggler --map map.txt inp1 > inp2  # replace u=0 with u=10
  > numjuggler --mode wrap inp2 > inp3    # ensure all lines shorter 80 chars.


Rename all cells and surfaces by adding 1000::

  > numjuggler -s 1000 -c 1000 inp > inp1
  > numjuggler --mode wrap inp1 > inp2    # ensure all lines shorter 80 chars.


Rename all cells and surfaces by incrementing numbers as they appear in the
input file. To check renumbering, store log and use it on the next step as the
map file to perform the reverse renumbering.  Finally, remove extra spaces from
the resulting file and original one, in order to simplify visual comparison::

  > numjuggler -c i -s i --log i1.log i1 > i2
  > numjuggler --map i1.log i2 > i3  # apply log as map for reverse renubmering
  > numjuggler --mode rems i1 > c1   # remove extra spaces from original input
  > numjuggler --mode rems i3 > c3   # and from result of reverse renumbering
  > vimdiff c1 c3                      # compare files visually



