#!/bin/bash
#
# check_lost_reads.sh
# Copyright (C) 2020 Oleksandr Moskalenko <om@rc.ufl.edu>
#
# Distributed under terms of the MIT license.


check_lost_reads.py \
    --alnSum1=galaxy/test-data/align_and_counts_test_data/W1118_G1_BWASplitSAM_summary.tabular \
    --alnSum2=galaxy/test-data/align_and_counts_test_data/W55_G2_BWASplitSAM_summary.tabular \
    --fq=galaxy/test-data/align_and_counts_test_data/W55_M_1_1.fastq \
    --out=check_for_lost_reads_BASE_test_data.tabular
