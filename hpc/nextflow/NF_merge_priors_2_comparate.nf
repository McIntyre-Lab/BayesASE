#!/usr/bin/env nextflow

/*
*    Nextflow script for merging priors to filtered and summarized ASE counts
*	ase counts can be generated using align_and_sam_compare module on DNA reads, simulated reads or RNA reads
*
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=path/to/user/temp_directory
*/

println """\
    DIRECTORIES AND INPUT FILES
    summarized ASE counts:          ${FILT}
    scripts:                        ${SCRIPTS}
    priors:                         ${PRIORS}
    design priors:	            ${DESIGN}
    design comparate:               ${DESIGN2}
    output for bayesian:            ${BAYESIN}
    """
    .stripIndent()


// // mine !{DF}/df_priors.csv
// G1,G2,sample
// W1118,W55,W55_M
// W1118,W55,W55_V


process mergePriors {

    output:
    env LIST into merge_ch

    shell:
    '''
    module load python3

    mkdir -p !{BAYESIN}
    echo "running merge priors to comparate
    "
    python3 !{SCRIPTS}/merge_priors_to_comparate_03amm.py \
        --output !{BAYESIN} \
        --comp !{FILT} \
        --prior !{PRIORS} \
        --design !{DESIGN}

    LIST=$(ls !{BAYESIN}/bayesian_input_*.csv)
    echo " list is :  ${LIST}"

    '''

}

// design file for comparing
//  Comparate_1,Comparate_2,compID
//  W55_M,W55_V,W55_M_V

process merge4Bayes {

    input:
    env LIST from merge_ch.collect()    
    
    shell:
    '''
    module load	python3

    python3 !{SCRIPTS}/merge_comparates_and_gen_headers_for_bayesian_02amm.py \
    --output !{BAYESIN} \
    --comp !{BAYESIN} \
    --design !{DESIGN2}

    '''
}

