#!/bin/sh
#SBATCH --mail-user=ammorse@ufl.edu
#SBATCH --job-name=prep
#SBATCH --account=mcintyre
#SBATCH --qos=mcintyre-b
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /blue/mcintyre/share/BASE_mclab/galaxy/test_scripts/SLURM_LOGS/prep.%A-%a.out
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --mem=20gb

## combine count tables
## summarize data



PROJ=/ufrc/mcintyre/share/BASE_mclab/galaxy
SCRIPTS=${PROJ}/scripts/ase_scripts
DF=${PROJ}/design_files
SAMC=${PROJ}/ase_counts_updated

SSUM=${PROJ}/ase_counts_updated_summed_techReps
FILT=${PROJ}/ase_counts_summarized_and_output_APN_values

BEDFILE=${PROJ}/references/BASE_testData_galaxy.bed
DESIGN=${PROJ}/design_files/df_BASE_galaxy_W55_noEmptyFq.csv


    # Load modules
    module loadpython/3.6 htslib

    mkdir -p ${SSUM}

    SIM=FALSE
    APN=1

    python3 ${SCRIPTS}/combine_cnt_tables_13amm.py \
        -design ${DESIGN} \
        -sim ${SIM} \
        --bed ${BEDFILE} \
        --path ${SAMC} \
        --designdir ${DF} \
        --out ${SSUM}


    ## design2 is created in above script
    DESIGN2=${DF}/df_ase_samcomp_summed.csv

    mkdir -p ${FILT}

    python3 ${SCRIPTS}/summarize_sam_compare_cnts_table_1cond_and_output_APN_05amm.py \
        --output ${FILT} \
        --design ${DESIGN2} \
        --parent1 G1 \
        --parent2 G2 \
        --sampleCol sample \
        --sampleIDCol sampleID \
        --sam-compare-dir ${SSUM} \
        --apn ${APN} \


