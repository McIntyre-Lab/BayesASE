#!/usr/bin/env bash

## 2 conditions - M vs V

## Set / Create Directories and Variables
SCRIPTS=hpc/stan2_scripts

## Create temp output directory for initial datafile with modified headers before entering Bayesian
ROZ=example_out/temp_directory
    mkdir -p $ROZ

## directory for model testing
BAYES=example_out/bayesian_in

BAYESOUT=example_out/bayesian_out
    mkdir -p $BAYESOUT

## Set design file with G1, G2, c1, c2, and input filename columns
DESIGN_FILE=example_in/comparate_design_file.csv

DESIGN=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $DESIGN_FILE)
IFS=',' read -ra ARRAY <<< "$DESIGN"

COMP_1=${ARRAY[0]}
COMP_2=${ARRAY[1]}
COMPID=${ARRAY[2]}

echo "comparate 1 is $COMP_1"

## Set number of comparates to be analyzed
	## M vs F for each line = 2
COMPNUM=2

## set number of iterations = 100,000
ITER=100000

## set burn in of 10,000
WARMUP=10000

######  Run python script calling environmental bayesian model (stan2, 2 conditions)
python3 $SCRIPTS/NBmodel_stan2_slurm_02amm.py \
    -comparate_1 $COMP_1 \
    -comparate_2 $COMP_2 \
    -c1_g1 M \
    -c1_g2 M \
    -c2_g1 V \
    -c2_g2 V \
    -compID $COMPID \
    -datafile $BAYES \
    -datafile2 $BAYESOUT/ \
    -cond $COMPNUM \
    -workdir . \
    -routput $BAYESOUT \
    -subpath $SCRIPTS/NBModel_stan2_flex_prior.R \
    -iterations $ITER \
    -warmup $WARMUP \
    -o $BAYESOUT
