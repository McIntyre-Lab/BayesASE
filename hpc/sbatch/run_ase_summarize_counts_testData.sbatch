#!/bin/sh
#SBATCH --mail-user=yourname@your.email
#SBATCH --job-name=prep
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o example_out/logs/prep.%A-%a.out
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --mem=20gb

## combine ase count tables
## summarize data


SCRIPTS=hpc/ase_scripts
SAMC=example_out/ase_counts_updated

SSUM=example_out/ase_counts_summed_techReps
    mkdir -p $SSUM
FILT=example_out/ase_counts_summarized
    mkdir -p $FILT

BEDFILE=example_out/snp_feature_first.bed
DESIGN=example_in/df_BASE_galaxy_W55_combinedFq.csv


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
        --designdir example_in \
        --out ${SSUM}


    ## design2 is created in above script
    DESIGN2=example_in/df_ase_samcomp_summed.csv

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
