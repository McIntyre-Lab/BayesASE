#!/bin/bash

TEST="check_comparate_design_file"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

check_comparate_design_file.py "$@" \
    --design galaxy/test-data/merge_priors_testdata/pre_bayesian_df_BASE.tsv \
    --compNum 2 \
    --out ${TESTDIR}/Pre_Bayesian_design_criteria.tabular

date
echo "### Finished test: ${TEST}"
