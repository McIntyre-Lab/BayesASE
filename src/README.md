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
