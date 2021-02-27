#!/bin/sh
#SBATCH --mail-user=yourname@your.email
#SBATCH --job-name=dfPrior
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /blue/mcintyre/share/BASE/scripts/SLURM_LOGS/dfPrior_%A.out
#SBATCH -t 01:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=1gb



### create design file for calculating priors from df_ase_samcomp_summed.dsv 

## Set / Create Directories and Variables
PROJ=/blue/mcintyre/share/BASE_mclab/galaxy
DF=$PROJ/design_files

DESIGN=$DF/df_ase_samcomp_summed.csv

awk 'BEGIN{FS=","; OFS=","} { print $1, $2, $4}' !{DESIGN} | sort -u > !{DF}/df_priors.csv
