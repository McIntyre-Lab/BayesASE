#!/bin/bash
date;hostname;pwd

#    <tests>
#        <test>
#            <param name="sum1" ftype="data"      value="Number_Rows_Left_After_Removed_Reads.tabular"/>
#            <param name="sum2" ftype="data"      value="Number_Rows_Left_After_Removed_Reads_G2.tabular"/>
#            <param name="ase"  ftype="data"      value="ASE_totals_table_BASE_test_data.tsv" />
#            <output name="out" file="check_SAM_compare_for_lost_reads_BASE_test_data.tabular" />
#        </test>
#    </tests>

TEST="check_samcomp_lost_reads"
TESTDIR="testout/${TEST}"
rm -rf ${TESTDIR}
mkdir -p ${TESTDIR}
echo "### Starting test: ${TEST}"

src/scripts/check_samcomp_lost_reads.py "$@" \
    --summary1 BASE_workflow_test_data/Number_Rows_Left_After_Removed_Reads.tabular \
    --summary2 BASE_workflow_test_data/Number_Rows_Left_After_remove_reads_G2.tabular \
    --ase_names galaxy/test-data/align_and_counts_test_data/ASE_totals_table_BASE_test_data.tsv \
    --ase galaxy/test-data/align_and_counts_test_data/ASE_totals_table_BASE_test_data.tsv \
    --out ${TESTDIR}/check_SAM_compare_for_lost_reads_BASE_test_data.tabular

date
echo "### Finished test: ${TEST}"
