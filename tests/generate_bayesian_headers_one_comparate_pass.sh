#!/bin/bash
date;hostname;pwd

#    <tests>
#        <test>
#            <param name="design" value="bayesian_input/comparate_df_one_condition.tsv" ftype="tsv"/>
#            <param name="collection" value="merge_priors_testdata/bayesian_input_W55_M" ftype="tabular"/>
#            <output_collection name="split_output" type="list">
#              <element name="FEATURE_ID">
#                <assert_contents>
#                  <has_text_matching expression="gen_headers_one_comparate"/>
#                </assert_contents>
#              </element>
#             </output_collection>
#        </test>
#    </tests>


TEST="generate_bayesian_headers_one_comparate"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

src/scripts/gen_headers_after_merge_priors_ONE_COMPARATE.py "$@" \
    --design galaxy/test-data/merge_priors_testdata/df_one_comparate.tsv \
    --collection_identifiers W55_M,M_V \
    --collection_filenames galaxy/test-data/merge_priors_testdata/merge_priors_to_comparate/bayesian_input_W55_M,galaxy/test-data/merge_priors_testdata/merge_priors_to_comparate/bayesian_input_W55_V \
    --output ${TESTDIR}

date
echo "### Finished test: ${TEST}"
