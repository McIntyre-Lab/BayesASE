#!/bin/sh
#SBATCH --mail-user=yourname@your.email
#SBATCH --job-name=calP
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o example_out/logs/calP_%A.out
#SBATCH -t 06:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=6gb

### (1) calculate priors from ASE count tables (generated from simulated reads, DNA reads, or RNA data reads)

# Load modules
module load python3
module load htslib

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
