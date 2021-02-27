#!/bin/sh
#SBATCH --mail-user=yourname@your.email
#SBATCH --job-name=merge
#SBATCH --account=mcintyre
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /blue/mcintyre/share/BASE_mclab/galaxy/scripts/SLURM_LOGS/merge.%j.out
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --mem=10gb



## merge priors to comparate
## merge comparates together


PROJ=/blue/mcintyre/share/BASE_mclab/galaxy
SCRIPTS=${PROJ}/scripts/ase_scripts
DF=${PROJ}/design_files

## user must provide following design file for merging comparates:
DESIGN2=${DF}/comparate_design_file_02amm.csv

DESIGN=${DF}/df_priors.csv
PRIORS=${PROJ}/priors_fromData
FILT=${PROJ}/ase_counts_summarized
BAYESIN=${PROJ}/bayesian_in
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


    python3 ${SCRIPTS}/merge_comparates_and_gen_headers_for_bayesian_03amm.py \
    --output ${BAYESIN} \
    --comp ${BAYESIN} \
    --design ${DESIGN2}


