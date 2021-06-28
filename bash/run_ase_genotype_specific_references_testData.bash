#!/usr/bin/env bash

## set directories
## All directories are relative to the main BayesASE folder
VCFIN=example_in/vcf_by_genotype
VCFOUT=example_out/vcf_by_genotype
UREF=example_out/reference/updated_genomes_vcfConsensus
mkdir -p $VCFOUT
mkdir -p $UREF

FASTA=example_in/reference/dmel_r551_chromosome_2R_X.fasta

# line,old
# W55,Winters_55
# W1118,w1118_w118
DESIGN_FILE=example_in/df_list_G2_VCF_split.csv
DESIGN=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $DESIGN_FILE)
IFS=',' read -ra ARRAY <<< "$DESIGN"

G2=${ARRAY[0]}

#### (1) UPDATE SNPs
### Index starting VCF files


    ## remove and replace if gz file already exists (so we can overwrite)
    if [[ -f ${VCFOUT}/${G2}_snp_testGenes_sorted.vcf.gz ]] ; then
        rm ${VCFOUT}/${G2}_snp_testGenes_sorted.vcf.gz
    fi

    # sort split VCF files
    bcftools sort -O v ${VCFIN}/${G2}_snp_testGenes.vcf -o ${VCFOUT}/${G2}_snp_testGenes_sorted.vcf

    echo "indexing individual SNP vcf files: ${G2} "
    bgzip ${VCFOUT}/${G2}_snp_testGenes_sorted.vcf
    tabix ${VCFOUT}/${G2}_snp_testGenes_sorted.vcf.gz

    echo "updating SNPs: ${G2} "
    cat ${FASTA} | vcf-consensus ${VCFOUT}/${G2}_snp_testGenes_sorted.vcf.gz > ${UREF}/${G2}_snp_upd_genome.fasta


    #### (2) Build indexes from the references
    echo `date`": building BWA index for ${G2} UPD genome "
    ##BWA-mem references  -p is the prefix for the output database, -a is the indexing algorithm ('bwtsw' is for ref>2G, 'is' for ref<2G).
    bwa index -p ${UREF}/${G2}_snp_upd_genome_BWA -a bwtsw ${UREF}/${G2}_snp_upd_genome.fasta

    echo `date`": building samtools index for ${G2} UPD genome"
    samtools faidx ${UREF}/${G2}_snp_upd_genome.fasta

	
	
