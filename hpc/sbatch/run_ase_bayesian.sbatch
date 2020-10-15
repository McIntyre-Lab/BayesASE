#!/bin/sh
#SBATCH --mail-user=ammorse@ufl.edu
#SBATCH --job-name=stan2_decoupled
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH --account=mcintyre
#SBATCH -o /blue/mcintyre/share/BASE_mclab/galaxy/scripts/SLURM_LOGS/stan2_decoupled.%A-%a.out
#SBATCH -t 1:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=10gb
#SBATCH --array=2

# Load modules
module purge
module load python/3.6 htslib R/3.6

## G3 testData!!!
## 2 conditions - M vs V

## Set / Create Directories and Variables
PROJ=/blue/mcintyre/share/BASE_mclab/galaxy
SCRIPTS=$PROJ/scripts/stan2_scripts

## Create temp output directory for initial datafile with modified headers before entering Bayesian
ROZ=$PROJ/roz_ammB
    mkdir -p $ROZ

## directory for model testing
BAYES=$PROJ/bayesian_in

BAYESOUT=$PROJ/bayesian_out
    mkdir -p $BAYESOUT

## Set design file with G1, G2, c1, c2, and input filename columns
DESIGN_FILE=$PROJ/design_files/comparate_design_file_02amm.csv

DESIGN=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $DESIGN_FILE)
IFS=',' read -ra ARRAY <<< "$DESIGN"

COMP_1=${ARRAY[4]}
COMP_2=${ARRAY[5]}
COMPID=${ARRAY[6]}


## Set number of comparates to be analyzed
	## M vs F for each line = 2
COMPNUM=2

## set number of iterations = 100,000
ITER=100000

## set burn in of 10,000
WARMUP=10000

######  Run python script calling environmental bayesian model (stan2, 2 conditions)
python3 $SCRIPTS/NBmodel_stan2_slurm_06amm.py \
    -comparate_1 $COMP_1 \
    -comparate_2 $COMP_2 \
    -compID $COMPID \
    -datafile $BAYES \
    -datafile2 $BAYESOUT/ \
    -cond $COMPNUM \
    -workdir '/blue/mcintyre/share/BASE_mclab/galaxy/scripts/stan2_scripts' \
    -routput $BAYESOUT \
    -subpath '/blue/mcintyre/share/BASE_mclab/galaxy/scripts/stan2_scripts/NBModel_stan2_flex_prior.R' \
    -iterations $ITER \
    -warmup $WARMUP \
    -o $BAYESOUT
