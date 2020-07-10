#!/usr/bin/env nextflow

/*
*    Nextflow script for prepping counts and running bayesian
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=/ufrc/mcintyre/share/cegs2_MvsF_exp/ROZ_NF
*/

println """\
    DIRECTORIES AND INPUT FILES
    input sam compare counts:     ${SAMC}
    output combined counts:       ${SSUM}
    output filtered counts:       ${FILT}
    output merged counts:         ${MERGE}
    output merged no APN columsn: ${DROP}

    design for combined counts:   ${DESIGN}
    design for summarizing:       ${DESIGN2}
    design for filtering:         ${DESIGN3}
    """
    .stripIndent()


process sumCnts {

    output:
    val FILE into filt_ch

    shell:
    '''

    module load python/3.8 htslib
    mkdir -p !{SSUM}

    echo "
        summing ase counts for all genotypes
    "
    ## running all, on data
    ## note user can specify specific rows to run using --begin and --end parameters (not required)
    python3 !{SCRIPTS}/combine_cnt_tables_13amm.py \
        -design !{DESIGN} \
        -sim !{SIM} \
        --bed !{BED} \
        --path !{SAMC} \
        --designdir !{DF} \
        --out ${SSUM}

    '''
}


process summarize {

    input:
    val FILE from filt_ch.collect()

    output:
    val FILE into merge_ch

    shell:
    '''

    module load python/3.6 htslib
    mkdir -p !{FILT}

    python3 !{SCRIPTS}/summarize_sam_compare_cnts_table_1cond_and_output_APN_05amm.py \
        --output !{FILT} \
        --design !{DESIGN2} \
        --parent1 G1 \
        --parent2 G2 \
        --sampleCol sample \
        --sampleIDCol sampleID \
        --sam-compare-dir !{SSUM} \
        --apn !{APN} \

    '''
}

process merge {

    input:
    val FILE from merge_ch.collect()
    
    output:
    val FILE into drop_ch

    shell:
    '''

    module load python/3.6 htslib
    mkdir -p !{MERGE}

    #### (1) merge comparate files based on rows in user provided design file to be analyzed by the Bayesian Model
    python3 !{SCRIPTS}/merge_comparates_for_bayesian_10brm.py \
        --output ${MERGE} \
        --comp !{FILT} \
        --design !{DESIGN3}

    '''

}

process drop {

    input:
    val FILE from drop_ch.collect()

    
    shell:
    '''
    module load python/3.6 htslib
    mkdir -p !{DROP}

    for FILE in !{MERGE}/*
    do
        echo -e "file is ${FILE}"
        python !{SCRIPTS}/drop_columns_w_APN_values.py \
            --output !{DROP} \
            --input ${FILE}
    done

    '''
}
