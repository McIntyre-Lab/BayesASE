#!/bin/bash
date;hostname;pwd

#<test>
#    <param name="design" ftype="data"     value="BASE_testdata/check_align_design_testdata/alignment_design_file.tsv"/>
#    <output name="dups"  ftype="data" file="BASE_testdata/check_align_design_testdata/alignment_design_file_duplicates.tabular" />
#    <output name="logfile"  ftype="data" file="BASE_testdata/check_align_design_testdata/alignment_design_file_criteria.csv" />
#</test>

TESTDIR="testout/check_aln_design_file"

rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}

src/scripts/check_aln_design_file.py.py "$@" \
	--design galaxy/test-data/align_and_counts_test_data/alignment_design_file.tsv \
    --dups 
    --output
date
