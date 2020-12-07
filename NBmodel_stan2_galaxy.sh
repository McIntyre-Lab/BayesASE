#!/bin/bash

#    <tests>
#        <test>
#            <param name="design" ftype="data" value="BASE_testdata/run_bayesian_testdata/comparate_df_two_conditions_BASE.tsv"/>
#            <param name="cond" ftype="text" value="2" />
#            <param name="iterations" ftype="text" value="100000" />
#            <param name="warmup" ftype="text" value="10000" />
#            <param name="collection">
#              <collection type="list">
#                <element name="collection" value="BASE_testdata/run_bayesian_testdata/bayesian_input_W55_M_V"/>
#              </collection>
#             </param>
#             <output_collection name="split_output" type="list">
#               <element name="comparison">
#                 <assert_contents>
#                   <has_text_matching expression="W55_M_V" />
#                  </assert_contents>
#                </element>
#              </output_collection>
#        </test>

# collection dir:  galaxy/test-data/nbmodel

TESTDIR="testout/nbmodel"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
python3 src/scripts/nbmodel_stan2.py \
    --design galaxy/test-data/bayesian_input/comparate_design_file.tsv \
    --collection_identifiers bayesian_input_W55_M_V \
    --collection_filenames galaxy/test-data/bayesian_input/bayesian_input_W55_M_V.tabular \
    --datafile2 ${TESTDIR} \
    --workdir src/scripts/ \
    --subpath src/scripts/nbmodel_stan2_flex_prior.R \
    -o ${TESTDIR} \
    -routput ${TESTDIR} \
    -cond 2 \
    -iterations 100000 \
    -warmup 10000
