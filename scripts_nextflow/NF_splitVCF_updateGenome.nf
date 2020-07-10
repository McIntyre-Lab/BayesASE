#!/usr/bin/env nextflow

/*
*    Nextflow script for updating genomes*
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=/ufrc/mcintyre/share/cegs2_MvsF_exp/ROZ_NF
*/

println """\
    DIRECTORIES AND INPUT FILES
    input vcf:               ${VCF}
    output split vcf files:  ${VCFOUT}
    output updated genomes:  ${UREF}
    design file:             ${DESIGN_FILE}
    """
    .stripIndent()


// split design file into 1 row chunks
// want to execute a task for each row
Channel
    .fromPath( DESIGN_FILE )
    .splitCsv( header: ['FQNAME','VCFNAME'], skip: 1 )
    .set { chunks_ch }


process splitVCF {

    input:
    val row from chunks_ch

    output:
    val row into upd_ch

    shell:
    '''
    
    module load gatk/4.1.4.0
    mkdir -p !{VCFOUT}

    echo "splitting out !{row.VCFNAME} !{row.FQNAME}"

    ### Split SNPs
    # -sn sample name, include this genotype
    gatk SelectVariants \
        -R !{FASTA} \
        -V !{VCF} \
        --output ${VCFOUT}/!{row.FQNAME}_snp.vcf \
        -sn !{row.VCFNAME} \
        --exclude-non-variants
    
    ## rename
    sed "s/!{row.VCFNAME}/!{row.FQNAME}/g" !{VCFOUT}/!{row.FQNAME}_snp.vcf > !{VCFOUT}/!{row.FQNAME}_snp_renamed.vcf

    '''
}


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
    if [[ -f !{VCFOUT}/!{row.FQNAME}_snp_renamed_sorted.vcf.gz ]] ; then
        rm !{VCFOUT}/!{row.FQNAME}_snp_renamed_sorted.vcf.gz
    fi

    # sort split VCF files
    bcftools sort -O v !{VCFOUT}/!{row.FQNAME}_snp_renamed.vcf -o !{VCFOUT}/!{row.FQNAME}_snp_renamed_sorted.vcf

    echo "indexing individual SNP vcf files: !{row.FQNAME} "
    bgzip !{VCFOUT}/!{row.FQNAME}_snp_renamed_sorted.vcf
    tabix !{VCFOUT}/!{row.FQNAME}_snp_renamed_sorted.vcf.gz

    echo "updating SNPs: !{row.FQNAME} "
    cat !{FASTA} | vcf-consensus !{VCFOUT}/!{row.FQNAME}_snp_renamed_sorted.vcf.gz > !{UREF}/!{row.FQNAME}_snp_upd_genome.fasta


    #### (2) Build indexes from the references
    echo `date`": building BWA index for !{row.FQNAME} UPD genome "
    ##BWA-mem references  -p is the prefix for the output database, -a is the indexing algorithm ('bwtsw' is for ref>2G, 'is' for ref<2G).
    bwa index -p !{UREF}/!{row.FQNAME}_snp_upd_genome_BWA -a bwtsw !{UREF}/!{row.FQNAME}_snp_upd_genome.fasta

    echo `date`": building samtools index for !{row.FQNAME} UPD genome"
    samtools faidx !{UREF}/!{row.FQNAME}_snp_upd_genome.fasta


    '''

}
