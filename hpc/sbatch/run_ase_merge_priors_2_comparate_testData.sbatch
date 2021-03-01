#!/bin/sh
#SBATCH --mail-user=yourname@your.email
#SBATCH --job-name=merge
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o example_out/logs/merge.%j.out
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --mem=10gb



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

    # Load modules
    module load python/3

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


