#!/usr/bin/env nextflow

/*
*    Nextflow script for running bayesian stan2 decoupled priors model
*
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=/blue/mcintyre/share/BASE_mclab/galaxy/ROZ_NF
*/

println """\
    DIRECTORIES AND INPUT FILES
    scripts:                        ${SCRIPTS}
    design file:	            ${DESIGN_FILE}
    input for bayesian:             ${BAYESIN}
    output for bayesian:            ${BAYESOUT}
    """
    .stripIndent()

//  design file
//  C1_G1,C1_G2,C2_G1,C2_G2,Comparate_1,Comparate_2,compID
//  W1118,W55,W118,W55,W55_M,W55_V,W55_M_V
// split design file into 1 row chunks
// want to execute a task for each row

Channel
    .fromPath( DESIGN_FILE )
    .splitCsv( header: ['C1_G1','C1_G2','C2_G1','C2_G2','COMP_1','COMP_2','COMPID'], skip: 1 )
    .set { chunks_ch }

process runBayesian {

    input:
    val row from chunks_ch

    shell:
    '''

    module load python/3.6 htslib R/3.6

    mkdir -p !{BAYESOUT}
    mkdir -p !{ROZ}

    echo "running bayesian
    "

    ######  Run python script calling environmental bayesian model (stan2, 2 conditions)
    python3 !{SCRIPTS}/NBmodel_stan2_slurm_02amm.py \
        -c1_g1 !{row.C1_G1} \
        -c1_g2 !{row.C1_G2} \
        -c2_g1 !{row.C2_G1} \
        -c2_g2 !{row.C2_G2} \
        -comparate_1 !{row.COMP_1} \
        -comparate_2 !{row.COMP_2} \
        -compID !{row.COMPID} \
        -datafile !{BAYESIN} \
        -datafile2 !{ROZ} \
        -cond !{COMPNUM} \
        -workdir '/blue/mcintyre/share/BASE_mclab/galaxy/scripts/stan2_scripts' \
        -routput !{BAYESOUT} \
        -subpath '/blue/mcintyre/share/BASE_mclab/galaxy/scripts/stan2_scripts/NBModel_stan2_flex_prior.R' \
        -iterations !{ITER} \
        -warmup !{WARMUP} \
        -o ${BAYESOUT}

    '''
}
