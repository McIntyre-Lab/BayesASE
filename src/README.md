Allelic imbalance (AI) indicates the presence of functional variation in cis
regulatory regions. Detecting cis regulatory differences using AI is
widespread, yet there is no formal statistical methodology that tests whether
AI differs between conditions. The testing for AI involves several complex
bioinformatics steps. BayesASE is a complete bioinformatics pipeline that
incorporates state-of-the-art error reduction techniques and a [flexible
Bayesian approach to estimating AI and formally comparing levels of AI between
conditions](https://www.g3journal.org/content/8/2/447.long). The modular
structure of BayeASE has been packaged as a [python
package](https://pypi.org/project/BayesASE/), [bioconda package]
(https://anaconda.org/bioconda/bayesase), Galaxy toolkit, made available in
Nextflow and as a collection of scripts for the SLURM workload manager in the
[BayesASE project repository on
github](https://github.com/McIntyre-Lab/BayesASE).

The model included with the package can formally test AI within one condition
for three or more replicates and can statistically compare differences in AI
across conditions. This includes reciprocal crosses, test-crosses, and
comparisons of GxE for the same genotype in replicated experiments. As gene
expression affects power for detection of AI, and as expression may vary
between conditions, the model explicitly takes coverage into account. The
proposed model has low type I and II error under several scenarios, and is
robust to large differences in coverage between conditions. The model included
with the package reports estimates of AI for each condition, and the
corresponding Bayesian evidence as well as a formal statistical evaluation of
AI between conditions. The package is completely modular and the
bioinformatics steps needed to map reads in a genotype specific manner can be
used as input for other statistical models of AI and other methods for read
counting can be used and the model described in Novelo et al. 2018 deployed.
This model represents an update to the R code provided with the publication as
the MCMC algorithm is now implemented in RSTAN (Stan Development Team (2020).
"RStan: the R interface to Stan." [R package version
2.21.2](http://mc-stan.org/) and bias is allowed to vary between conditions
and more than 2 conditions can be compared. This is a very general
implementation.

## Overview

The workflow is summarized in this figure. Details can be found in the guide for the [Galaxy implementation](docs/BayesASE_Galaxy_User_Guide.pdf).

![Workflow](docs/Workflow.png)

## Quick demo
If you would like to try if you have all the needed software, you can run this few lines of code.

We suggest that at first you clone our repo in one folder of your choice. This will ensure you have all the needed test input files and scripts in the correct place. 

Clone repo:
    
    git clone https://github.com/McIntyre-Lab/BayesASE.git

The input files needed to run the test data are in the example_in folder. The results will be stored in the example_out folder.
	
Run the demo steps in the specified order.

    sbatch hpc/sbatch/run_ase_genotype_specific_references_testData.sbatch
	
	sbatch hpc/sbatch/run_ase_align_and_count_testData.sbatch
	
	sbatch hpc/sbatch/run_ase_summarize_counts_testData.sbatch

	sbatch hpc/sbatch/run_ase_create_design_file_4_prior_calc.sbatch

	sbatch hpc/sbatch/run_ase_prior_calculation_testData.sbatch
	
	sbatch hpc/sbatch/run_ase_merge_priors_2_comparate_testData.sbatch

    sbatch hpc/sbatch/run_ase_bayesian.sbatch

