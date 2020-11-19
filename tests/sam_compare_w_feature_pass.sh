#!/bin/bash
#         <test>
#            <param name="fastq" ftype="data"      value="W55_M_1_1.fastq"/>
#            <param name="sama"  ftype="data"     value="W1118_G1_create_new_SAM_file_with_features_BASE_test_data.sam"/>
#            <param name="samb"  ftype="data"     value="W55_G2_create_new_SAM_file_with_features_BASE_test_data.sam" />
#            <param name="feature" ftype="data"   value="reformat_BED_file_for_BASE.bed" />
#            <param name="nofqids" ftype="select"   value="true" />
#            <output name="counts"    file="ASE_counts_table_BASE_test_data.tsv" />
#            <output name="totals"    file="ASE_totals_table_BASE_test_data.tsv" />
#        </test>
# length from `awk '{if(NR%4==2 && length) {count++; bases += length}} END {print
TESTDIR="testout/sam_compare_w_feature"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
src/scripts/sam_compare_w_feature.py \
    --fastq galaxy/test-data/align_and_counts_test_data/W55_M_1_1.fastq \
    --sama galaxy/test-data/align_and_counts_test_data/W1118_G1_create_new_SAM_file_with_features_BASE_test_data.sam \
    --samb galaxy/test-data/align_and_counts_test_data/W55_G2_create_new_SAM_file_with_features_BASE_test_data.sam \
    --feature galaxy/test-data/align_and_counts_test_data/reformat_BED_file_for_BASE.bed \
    --length 96 \
    --nofqids \
    --counts ${TESTDIR}/ASE_counts_table_BASE_test_data.tsv \
    --totals ${TESTDIR}/ASE_totals_table_BASE_test_data.tsv \
    -g stdout
