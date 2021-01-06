#!/bin/bash
TEST="check_sam_present"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

src/scripts/check_sam_present.py "$@" \
    --fq galaxy/test-data/align_and_counts_test_data/W55_M_1_1.fastq \
    --alnType SE \
    --sam1 galaxy/test-data/align_and_counts_test_data/W1118_G1_unique_sam_for_BASE.sam \
    --sam2 galaxy/test-data/align_and_counts_test_data/W55_G2_unique_sam_for_BASE.sam \
    --out ${TESTDIR}/check_SAM_present_BASE_test_data.tabular

date
echo "### Finished test: ${TEST}"
