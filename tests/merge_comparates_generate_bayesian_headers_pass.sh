#!/bin/bash
date;hostname;pwd

#<test>
#    <param name="design" value="BASE_testdata/merge_priors_testdata/df_comparate.tsv" ftype="tsv"/>
#    <param name="collection" value="BASE_testdata/merge_priors_testdata/merge_priors_to_comparate" ftype="data_collection"/>
#    <output_collection name="split_output" type="list">
#      <element name="FEATURE_ID">
#        <assert_contents>
#          <has_text_matching expression="Merge_comparates_and_gen_headers"/>
#        </assert_contents>
#      </element>
#     </output_collection>
#</test>

TEST="merge_comparates_generate_bayesian_headers"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

src/scripts/merge_comparates_generate_bayesian_headers.py "$@" \
    --design ./galaxy/test-data/merge_priors_testdata/df_comparate.tsv \
    --collection_identifiers W55_M,W55_V \
    --collection_filenames galaxy/test-data/merge_priors_testdata/merge_priors_to_comparate/bayesian_input_W55_M,galaxy/test-data/merge_priors_testdata/merge_priors_to_comparate/bayesian_input_W55_V \
    --output ${TESTDIR}

date
echo "### Finished test: ${TEST}"
