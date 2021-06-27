#!/usr/bin/env bash

### create design file for calculating priors from df_ase_samcomp_summed.dsv 

## Set / Create Directories and Variables
DF=example_out
DESIGN=example_in/df_ase_samcomp_summed.csv

awk 'BEGIN{FS=","; OFS=","} { print $1, $2, $4}' ${DESIGN} | sort -u > ${DF}/df_priors.csv
