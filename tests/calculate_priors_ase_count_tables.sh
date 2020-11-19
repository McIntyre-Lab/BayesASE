#!/bin/bash
date;hostname;pwd
# <test>
#     <param name="design" value="reformat_df_BASE_test_data.tsv" ftype="tsv"/>
#     <param name="collection">
#       <collection type="list">
#         <element name="FEATURE_ID" value="BASE_testdata/summarize_counts_testdata/filtered_ASE_counts_tables_BASE"/>
#       </collection>
#      </param>
#      <output_collection name="split_output" type="list">
#        <element name="FEATURE_ID">
#          <assert_contents>
#            <has_text_matching expression="Calculated_priors" />
#           </assert_contents>
#         </element>
#       </output_collection>
# </test>

TESTDIR="testout/calculate_priors_ase_count_tables"

rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}

src/scripts/calculate_priors_ase_count_tables.py "$@" \
    --design galaxy/test-data/summarize_counts_testdata/sample_design_file.tabular \
    --collection_identifiers W55_M,W55_V \
    --collection_filenames galaxy/test-data/summarize_counts_testdata/filtered_ASE_counts_tables_BASE/ase_counts_filtered_W55_M,galaxy/test-data/summarize_counts_testdata/filtered_ASE_counts_tables_BASE/ase_counts_filtered_W55_V \
    --output ${TESTDIR}

date
