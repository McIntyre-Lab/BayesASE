#!/bin/sh
#SBATCH --mail-user=ammorse@ufl.edu
#SBATCH --job-name=calP
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /ufrc/mcintyre/share/BASE/scripts/SLURM_LOGS/calP_%A.out
#SBATCH -t 06:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=6gb
#SBATCH --array=2

### (1) calculate priors from ASE count tables (generated from simulated reads, DNA reads, or RNA data reads)

# Load modules
module load python3
module load htslib

## Set / Create Directories and Variables
PROJ=/ufrc/mcintyre/share/BASE_mclab
SCRIPTS=$PROJ/galaxy/scripts

FILT=$PROJ/ase_counts_summarized

PRIOR=$PROJ/priors 
    if [ ! -e $PRIOR ]; then mkdir -p $PRIOR; fi

## Set design file directory
DF=$PROJ/design_files/
DESIGN=$DF/df_priors.csv

##### (1) calculate priors from ASE tables

python3 $SCRIPTS/calculate_priors_from_ase_count_tables_03amm.py \
    --output $PRIOR \
    --design $DESIGN \
    --input $FILT \
    --debug
