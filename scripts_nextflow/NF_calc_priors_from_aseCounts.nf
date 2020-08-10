#!/usr/bin/env nextflow

/*
*    Nextflow script for calculating priors from filtered and summarized ASE counts
*	ase counts can be generated using align_and_sam_compare module on DNA reads, simulated reads or RNA reads
*
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=/ufrc/mcintyre/share/BASE_mclab/galaxy/ROZ_NF
*/

println """\
    DIRECTORIES AND INPUT FILES
    summarized ASE counts for calculating priors:    ${PCNTS}
    scripts:                                         ${SCRIPTS}
    output dir for priors:                           ${PRIORS}
    design file:	                             ${DESIGN}
    """
    .stripIndent()


// Brecca's current prior df:
// G1,     G2,    sampleID,    prior_file
// W1118,  R321,  mel_R321_M,  mel_R321_M_priors

// below is df for summarizing (df_ase_samcomp_summed.csv):
// G1,G2,sampleID,sample
// W1118,W55,W55_M_1,W55_M
// W1118,W55,W55_M_2,W55_M
// W1118,W55,W55_M_3,W55_M

// drop samplID col from df_ase_samcop_summed.csv and uniq.


process df_prep {

    shell:
    '''
    
    awk 'BEGIN{FS=","; OFS=","} { print $1, $2, $4}' !{DESIGN} | sort -u > !{DF}/df_priors.csv

    '''

}

process calcPriors {

    shell:
    '''
    module load python3 htslib

    mkdir -p !{PRIORS}

    python3 !{SCRIPTS}/calculate_priors_from_ase_count_tables_03amm.py \
    --output !{PRIORS} \
    --design !{DF}/df_priors.csv \
    --input !{PCNTS} \
    --debug

    '''
}
