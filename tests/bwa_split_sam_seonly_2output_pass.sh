#!/bin/bash
date;hostname;pwd
# <test>
#     <param name="sam" ftype="data"      value="bam_to_sam_BASE_test_data.sam"/>
#     <output name="uniq" ftype="data"      value="W1118_G1_unique_sam_for_BASE.sam"/>
#     <output name="summ"     file="W1118_G1_BWASplitSAM_summary.tabular" />
# </test>

TEST="bwa_split_sam_seonly_2output"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

../src/scripts/bwa_split_sam_seonly_2output.py "$@" \
    --sam ../galaxy/test-data/align_and_counts_test_data/bam_to_sam_BASE_test_data.sam \
    --uniq ${TESTDIR}/W1118_G1_unique_sam_for_BASE.sam \
    --summ ${TESTDIR}/W1118_G1_BWASplitSAM_summary.tabular

date
echo "### Finished test: ${TEST}"
