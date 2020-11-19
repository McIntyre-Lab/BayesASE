#! /bin/sh
#
# check_samcomp_lost_reads.sh
# Copyright (C) 2020 Oleksandr Moskalenko <om@rc.ufl.edu>
#
# Distributed under terms of the MIT license.
#

check_samcomp_lost_reads.py \
    --bwa1=galaxy/test-data/align_and_counts_test_data/W1118_G1_BWASplitSAM_summary.tabular \
    --bwa2=galaxy/test-data/align_and_counts_test_data/W55_G2_BWASplitSAM_summary.tabular \
    --fq=galaxy/test-data/align_and_counts_test_data/W55_M_1_1.fastq \
    --ase=galaxy/test-data/align_and_counts_test_data/ASE_totals_table_BASE_test_data.tsv \
    --out=check_SAM_compare_for_lost_reads_BASE_test_data.tabular
