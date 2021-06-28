#!/usr/bin/env bash

### (1) calculate priors from ASE count tables (generated from simulated reads, DNA reads, or RNA data reads)

## Set / Create Directories and Variables
SCRIPTS=hpc/ase_scripts

## this example calculates from data
FILT=example_out/ase_counts_summarized

OUTPUT=example_out/priors_fromData
mkdir -p $OUTPUT

DESIGN=example_out/df_priors.csv

##### (1) calculate priors from ASE counts - data

python3 $SCRIPTS/calculate_priors_from_ase_count_tables_03amm.py \
    --output $OUTPUT \
    --design $DESIGN \
    --input $FILT \
    --debug
