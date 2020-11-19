#!/bin/bash
date;hostname;pwd

# <test>
#     <param name="design" value="BASE_testdata/summarize_counts_testdata/priors_design_file.tsv" ftype="tsv"/>
#     <param name="collection1" value="/BASE_testdata/summarize_counts_testdata/summarized_and_filtered_ASE_counts_tables_BASE" ftype="data_collection"/>
#     <param name="collection2" value="BASE_testdata/calculated_priors_BASE_testdata" ftype="data_collection"/>
#     <output_collection name="split_output" type="list">
#       <element name="FEATURE_ID">
#         <assert_contents>
#           <has_text_matching expression="Merge_prior_to_comparate_test_data"/>
#         </assert_contents>
#       </element>
#      </output_collection>_
# </test>

TESTDIR="testout/merge_priors_to_comparate"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}

src/scripts/merge_priors_to_comparate.py "$@" \
	--design galaxy/test-data/summarize_counts_testdata/priors_design_file.tsv \
	-i1 W55_M,W55_V \
	-f1 galaxy/test-data/summarize_counts_testdata/summarized_and_filtered_ASE_counts_tables_BASE/ase_counts_filtered_W55_M,galaxy/test-data/summarize_counts_testdata/summarized_and_filtered_ASE_counts_tables_BASE/ase_counts_filtered_W55_V \
	-i2 W55_M_prior,W55_V_prior \
	-f2 galaxy/test-data/merge_priors_testdata/calculated_priors/W55_M_prior,galaxy/test-data/merge_priors_testdata/calculated_priors/W55_V_prior \
	--out ${TESTDIR}

date
