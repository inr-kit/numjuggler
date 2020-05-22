# Description

Change cell densities according to the map file. 

In the map file one can specify coefficients to multiply the original input
file densities. The coefficients can be specified for particular cells and/or
materials (or their ranges -- see descritpion of the map file format). 

## Rationale

One of the approaches to get the first guess for the 
weight-window mesh through the model geometry is to decrease
material densities for all cells between the source and tally region by several orders of magnitude and 
perform particle transport to generate the weight-window mesh. Experience shows that the obtained weight-window mesh
applied to the original (i.e. with nominal densities) model allready helps to improve statistics. 


## Invocation example

in the following example, the map file is `densities.txt`, the original input
file is `input.orig` and the new input file is written to `input.new`:

```bash
>numjuggler --mode cdens --map densities.txt input.orig > input.new
```

The content of `densities.txt`:

    c 1 -- 10: 0.01  # In cells 1 to 10 multiply density by 0.01
    c 12: 0.1        # Multiply cell 12 density by 0.1

    m 5: 1e-3        # For all cells filled with material 5 multiply density by 1e-3


UPD 2020.05.22: format specifier can be added as the last entry on the line in the map file. The format specifier is passed as a string and its `.format()` method is used
to convert density to string representation. For example (compare with above):

    c 1 -- 10: 0.01  {:7.3f} # Specify format for new densities
    c 12: 0.1                # Use default formatting
    
    m 5: 1e-3        {:10.3e}  # Specify format
