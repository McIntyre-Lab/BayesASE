#!/usr/bin/env bash

## merge priors to comparate
## merge comparates together


SCRIPTS=hpc/ase_scripts

## user must provide following design file for merging comparates:
DESIGN2=example_in/df_merge_comparates_4_bayesian.csv

DESIGN=example_out/df_priors.csv
PRIORS=example_out/priors_fromData
FILT=example_out/ase_counts_summarized
BAYESIN=example_out/bayesian_in
    mkdir -p $BAYESIN

    echo "running merge priors to comparate
    "
    python3 ${SCRIPTS}/merge_priors_to_comparate_03amm.py \
        --output ${BAYESIN} \
        --comp ${FILT} \
        --prior ${PRIORS} \
        --design ${DESIGN}


    python3 ${SCRIPTS}/merge_comparates_and_gen_headers_for_bayesian_02amm.py \
    --output ${BAYESIN} \
    --comp ${BAYESIN} \
    --design ${DESIGN2}


