#!/bin/sh
#SBATCH --mail-user=yourname@your.email
#SBATCH --job-name=prep
#SBATCH --account=mcintyre
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /blue/mcintyre/share/BASE_mclab/galaxy/scripts/SLURM_LOGS/prep.%A-%a.out
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --mem=20gb

## combine ase count tables
## summarize data


PROJ=.
SCRIPTS=${PROJ}/scripts/ase_scripts
DF=${PROJ}/design_files
SAMC=${PROJ}/ase_counts_updated

SSUM=${PROJ}/ase_counts_summed_techReps
    mkdir -p $SSUM
FILT=${PROJ}/ase_counts_summarized
    mkdir -p $FILT

BEDFILE=${PROJ}/references/BASE_testData_galaxy_02amm.bed
DESIGN=${PROJ}/design_files/df_BASE_galaxy_W55_combinedFq.csv


    # Load modules
    module load python/3.6 htslib

    mkdir -p ${SSUM}

    SIM=False
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

    python3 ${SCRIPTS}/summarize_sam_compare_cnts_table_1cond_and_output_APN_06amm.py \
        --output ${FILT} \
        --design ${DESIGN2} \
        --parent1 G1 \
        --parent2 G2 \
        --sampleCol sample \
        --sampleIDCol sampleID \
        --sam-compare-dir ${SSUM} \
        --apn ${APN} \
