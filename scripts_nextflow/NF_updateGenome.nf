#!/usr/bin/env nextflow

/*
*    Nextflow script for test data
*	fasta reference - only X and 2R
*	update
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=/ufrc/mcintyre/share/BASE_mclab/galaxy/ROZ_NF
*/

println """\
    DIRECTORIES AND INPUT FILES
    output split vcf files:	  	${VCF}
    output ref and updated genomes:	${UREF}
    design file:            		${DESIGN_FILE}
    """
    .stripIndent()


// split design file into 1 row chunks
// want to execute a task for each row
Channel
    .fromPath( DESIGN_FILE )
    .splitCsv( header: ['FQNAME','VCFNAME'], skip: 1 )
    .set { upd_ch }


process updGenomes {

    input:
    val row from upd_ch    

    shell:
    '''
    module load htslib/1.8 bcftools/1.10.2.1 vcftools/0.1.16 bwa/0.7.17 samtools/1.10

    mkdir -p !{UREF}
    mkdir -p !{ROZ}
 
    #### (1) UPDATE SNPs
    ### Index starting VCF files

    ## remove and replace if gz file already exists (so we can overwrite)
#    if [[ -f !{VCF}/!{row.FQNAME}_snp_testGenes.vcf.gz ]] ; then
#        rm !{VCF}/!{row.FQNAME}_snp_testGenes.vcf.gz
#    fi

    # sort split VCF files
    bcftools sort -O v !{VCF}/!{row.FQNAME}_snp_testGenes.vcf -o !{VCF}/!{row.FQNAME}_snp_testGenes_sorted.vcf

    echo "indexing individual SNP vcf files: !{row.FQNAME} "
    bgzip !{VCF}/!{row.FQNAME}_snp_testGenes_sorted.vcf
    tabix !{VCF}/!{row.FQNAME}_snp_testGenes_sorted.vcf.gz

    echo "updating SNPs: !{row.FQNAME} "
    cat !{FASTA} | vcf-consensus !{VCF}/!{row.FQNAME}_snp_testGenes_sorted.vcf.gz > !{UREF}/!{row.FQNAME}_snp_upd_genome.fasta


    #### (2) Build indexes from the references
    echo `date`": building BWA index for !{row.FQNAME} UPD genome "
    ##BWA-mem references  -p is the prefix for the output database, -a is the indexing algorithm ('bwtsw' is for ref>2G, 'is' for ref<2G).
    bwa index -p !{UREF}/!{row.FQNAME}_snp_upd_genome_BWA -a bwtsw !{UREF}/!{row.FQNAME}_snp_upd_genome.fasta

    echo `date`": building samtools index for !{row.FQNAME} UPD genome"
    samtools faidx !{UREF}/!{row.FQNAME}_snp_upd_genome.fasta


    '''

}
