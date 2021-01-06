#!/bin/bash
date;hostname;pwd

#<test>
#    <param name="design" ftype="data"     value="BASE_testdata/check_align_design_testdata/alignment_design_file.tsv"/>
#    <output name="dups"  ftype="data" file="BASE_testdata/check_align_design_testdata/alignment_design_file_duplicates.tabular" />
#    <output name="logfile"  ftype="data" file="BASE_testdata/check_align_design_testdata/alignment_design_file_criteria.csv" />
#</test>
TEST="check_aln_design_file"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

src/scripts/check_aln_design_file.py "$@" \
    --design galaxy/test-data/align_and_counts_test_data/alignment_design_file.tsv \
    --dups BASE_workflow_test_data/alignment_design_file_duplicates.tabular \
    --output ${TESTDIR}/alignment_design_file_criteria.csv

date
echo "### Finished test: ${TEST}"
