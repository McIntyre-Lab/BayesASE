#!/bin/bash
#We can remove the tests directory

#First to be run. 
sbatch hpc/sbatch/run_ase_align_and_count_testData.sbatch

sbatch hpc/sbatch/run_ase_bayesian.sbatch