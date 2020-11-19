#!/bin/bash

TESTDIR="testout/combine_count_tables_sim"
rm -rf ${TESTDIR}

src/scripts/combine_count_tables.py "$@" \
    --sim \
    --design galaxy/test-data/summarize_counts_testdata/alignment_design_test_file.tsv \
    --bed galaxy/test-data/align_and_counts_test_data/BASE_testData_BEDfile.bed \
    --collection_identifiers SRR1989589,SRR1990512_1,SRR1991135,SRR1991140_1,SRR1991611_1,SRR1991617_1 \
    --collection_filenames galaxy/test-data/summarize_counts_testdata/ASE_counts_tables/SRR1989589.fastq,galaxy/test-data/summarize_counts_testdata/ASE_counts_tables/SRR1990512_1.fastq,galaxy/test-data/summarize_counts_testdata/ASE_counts_tables/SRR1991135.fastq,galaxy/test-data/summarize_counts_testdata/ASE_counts_tables/SRR1991140_1.fastq,galaxy/test-data/summarize_counts_testdata/ASE_counts_tables/SRR1991611_1.fastq,galaxy/test-data/summarize_counts_testdata/ASE_counts_tables/SRR1991617_1.fastq \
    --outdir=${TESTDIR} \
    --outdesign design
