#!/usr/bin/env nextflow

/*
*    Nextflow script for prepping counts
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=/ufrc/mcintyre/share/BASE_mclab/galaxy/ROZ_NF
*/

println """\
    DIRECTORIES AND INPUT FILES
    input sam compare counts:     ${SAMC}
    output combined counts:       ${SSUM}
    output filtered counts:       ${FILT}

    design for combined counts:   ${DESIGN}
    """
    .stripIndent()



process sumCnts {

    output:
    env LIST into sum_ch 

    shell:
    '''
    module load python/3.8 htslib
    mkdir -p !{SSUM}

    ## running all, on data
    ## note user can specify specific rows to run using --begin and --end parameters (not required)
    python3 !{SCRIPTS}/combine_cnt_tables_13amm.py \
        -design !{DESIGN} \
        -sim !{SIM} \
        --bed !{BEDFILE} \
        --path !{SAMC} \
        --designdir !{DF} \
        --out !{SSUM}

    LIST=$(ls !{SSUM}/*.csv)
    echo " list is :  ${LIST} "
    
    '''
}

process summarize {

    input:
    env LIST from sum_ch

    shell:
    '''
    DESIGN2=!{DF}/df_ase_samcomp_summed.csv
    
    module load python/3.6 htslib
    mkdir -p !{FILT}

    python3 !{SCRIPTS}/summarize_sam_compare_cnts_table_1cond_and_output_APN_06amm.py \
        --output !{FILT} \
        --design ${DESIGN2} \
        --parent1 G1 \
        --parent2 G2 \
        --sampleCol sample \
        --sampleIDCol sampleID \
        --sam-compare-dir !{SSUM} \
        --apn !{APN} \


    '''
}

