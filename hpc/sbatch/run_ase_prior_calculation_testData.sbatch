#!/bin/sh
#SBATCH --mail-user=ammorse@ufl.edu
#SBATCH --job-name=calP
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /blue/mcintyre/share/BASE_mclab/galaxy/scripts/SLURM_LOGS/calP_%A.out
#SBATCH -t 06:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=6gb

### (1) calculate priors from ASE count tables (generated from simulated reads, DNA reads, or RNA data reads)

# Load modules
module load python3
module load htslib

## Set / Create Directories and Variables
PROJ=/blue/mcintyre/share/BASE_mclab/galaxy
SCRIPTS=$PROJ/scripts/ase_scripts
DF=$PROJ/design_files

## this example calculates from data
FILT=$PROJ/ase_counts_summarized

OUTPUT=$PROJ/priors_fromData
    if [ ! -e $PRIOR ]; then mkdir -p $PRIOR; fi

DESIGN=$DF/df_priors.csv

##### (1) calculate priors from ASE counts - data

python3 $SCRIPTS/calculate_priors_from_ase_count_tables_03amm.py \
    --output $OUTPUT \
    --design $DESIGN \
    --input $FILT \
    --debug
