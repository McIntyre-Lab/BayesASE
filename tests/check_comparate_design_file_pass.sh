#!/bin/bash
#
# check_lost_reads.sh
# Copyright (C) 2020 Oleksandr Moskalenko <om@rc.ufl.edu>
#
# Distributed under terms of the MIT license.

TEST_DIR="galaxy/test-data"

if [[ $# -eq 2 ]]; then
    IN_FILE=$1
else
    IN_FILE="${TEST_DIR}/merge_priors_testdata/pre_bayesian_df_BASE.tsv"
fi

check_comparate_design_file.py \
    --design=${IN_FILE} \
    --compNum=2 \
    --out=Pre_Bayesian_design_criteria.tabular

