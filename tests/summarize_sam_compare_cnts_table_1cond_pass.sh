#!/bin/bash
date;hostname;pwd
#         <test>
#            <param name="design" value="BASE_testdata/summarize_counts_testdata/summarization_df_BASE.tabular" ftype="tabular"/>
#            <param name="collection" value="BASE_testdata/summarize_counts_testdata/combined_ASE_counts_tables_BASE" ftype="data_collection"/>
#            <param name="parent1" value="G1" ftype="text"/>
#            <param name="parent2" value="G2" ftype="text"/>
#            <param name="sampleIDcol" value="sampleID" ftype="text"/>
#            <param name="samplecol" value="comparate" ftype="text"/>
#            <param name="apn" value="1" ftype="text"/>
#            <output_collection name="split_output" type="list">
#              <element name="FEATURE_ID">
#                <assert_contents>
#                  <has_text_matching expression="Summarize_ASE_counts_test_data"/>
#                </assert_contents>
#              </element>
#             </output_collection>
#        </test>

# Collection dir: galaxy/test-data/summarize_counts_testdata/combined_ASE_counts_tables_BASE
# W55_M_1  W55_M_1.fastq  W55_M_2  W55_M_2.fastq  W55_V_1  W55_V_1.fastq  W55_V_2  W55_V_2.fastq

TEST="summarize_sam_compare_cnts_table_1cond"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

src/scripts/summarize_sam_compare_cnts_table_1cond.py "$@" \
    --design galaxy/test-data/summarize_counts_testdata/summarization_df_BASE.tabular \
    --collection_identifiers W55_M_1,W55_M_2,W55_V_1,W55_V_2 \
    --collection_filenames galaxy/test-data/summarize_counts_testdata/combined_ASE_counts_tables_BASE/W55_M_1.fastq,galaxy/test-data/summarize_counts_testdata/combined_ASE_counts_tables_BASE/W55_M_2.fastq,galaxy/test-data/summarize_counts_testdata/combined_ASE_counts_tables_BASE/W55_V_1.fastq,galaxy/test-data/summarize_counts_testdata/combined_ASE_counts_tables_BASE/W55_V_2.fastq \
    --parent1 "G1" \
    --parent2 "G2" \
    --sampleCol "sample" \
    --sampleIDCol "sampleID" \
    --apn 1 \
    --out ${TESTDIR}

date
echo "### Finished test: ${TEST}"
