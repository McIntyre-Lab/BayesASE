Allelic imbalance (AI) occurs when alleles in a diploid individual are differentially expressed and
indicates cis acting regulatory variation. What is the distribution of allelic effects in a natural
population? Are all alleles the same? Are all alleles distinct? Tests of allelic effect are
performed by crossing individuals and comparing expression between alleles directly in the F1.
However, a crossing scheme that compares alleles pairwise is a prohibitive cost for more than a
handful of alleles as the number of crosses is at least (n2-n)/2 where n is the number of alleles.
We show here that a testcross design followed by a hypothesis test of AI between testcrosses can be
used to infer differences between non-tester alleles, allowing n alleles to be compared with n
crosses. Using a mouse dataset where both testcrosses and direct comparisons have been performed,
we show that ~75% of the predicted differences between non-tester alleles are validated in a
background of ~10% differences in AI. The testing for AI involves several complex bioinformatics
steps. BASE is a complete bioinformatics pipeline that incorporates state-of-the-art error
reduction techniques and a flexible Bayesian approach to estimating AI and formally comparing
levels of AI between conditions. In the mouse data, the direct test identifies more cis effects
than the testcross. Cis-by-trans interactions with trans-acting factors on the X contributing to
observed cis effects in autosomal genes in the direct cross remains a possible explanation for the
discrepancy. BASE is available as python and conda packages. Galaxy tools and workflows as well as
a Nextflow workflow are also included. BayesASE code is available from the [BayesASE GitHub
Repository](https://github.com/McIntyre-Lab/BayesASE).
