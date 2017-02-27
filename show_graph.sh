#!/bin/bash

what="numjuggler"

# Generate graph of imports
sfood -v -r --internal ./$what/main.py > $what.sfood1
sfood-cluster -f $what.clusters < $what.sfood1 > $what.sfood2
sfood-graph < $what.sfood2 > $what.dot
dot -v -Tpdf \
    -Gsize="11.692, 8.267!" \
    -Granksep="0.01" \
    -Gsep="1.0" \
    -Goverlap="true"  \
    -Gratio="compress" \
    -Gfontsize="8" \
    -Nshape="plaintext" \
    -Nfontsize="16" \
    -Earrowsize="0.5" \
    < $what.dot > $what.pdf
