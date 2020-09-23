#!/bin/sh
#SBATCH --mail-user=ammorse@ufl.edu
#SBATCH --job-name=upd
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /blue/mcintyre/share/BASE/scripts/SLURM_LOGS/upd_%A.out
#SBATCH -t 06:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --mem=6gb
#SBATCH --array=2


### update genomes

# Load modules
htslib/1.8 bcftools/1.10.2.1 vcftools/0.1.16 bwa/0.7.17 samtools/1.10

## set directories
PROJ=/blue/mcintyre/share/BASE_mclab/galaxy
ROZ=${PROJ}/rozUPD
VCF=${PROJ}/vcf_by_genotype
UREF=${PROJ}/updated_genomes_vcfConsensus
INPUT=${PROJ}/test_input

FASTA=${PROJ}/test_input/dmel_r551_chromosome_2R_X.fasta


DESIGN_FILE=${PROJ}/test_input/df_list_G2_VCF_split.csv
DESIGN=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $DESIGN_FILE)
IFS=',' read -ra ARRAY <<< "$DESIGN"

G2=${ARRAY[0]}


#### (1) UPDATE SNPs
### Index starting VCF files


    ## remove and replace if gz file already exists (so we can overwrite)
    if [[ -f ${VCF}/${G2}_snp_testGenes.vcf.gz ]] ; then
        rm ${VCF}/${G2}_snp_testGenes.vcf.gz
    fi

    # sort split VCF files
    bcftools sort -O v ${VCF}/${G2}_snp_testGenes.vcf -o ${VCF}/${G2}_snp_testGenes_sorted.vcf

    echo "indexing individual SNP vcf files: ${G2} "
    bgzip ${VCF}/${G2}_snp_testGenes_sorted.vcf
    tabix ${VCF}/${G2}_snp_testGenes_sorted.vcf.gz

    echo "updating SNPs: ${G2} "
    cat ${FASTA} | vcf-consensus ${VCF}/${G2}_snp_testGenes_sorted.vcf.gz > ${UREF}/${G2}_snp_upd_genome.fasta


    #### (2) Build indexes from the references
    echo `date`": building BWA index for ${G2} UPD genome "
    ##BWA-mem references  -p is the prefix for the output database, -a is the indexing algorithm ('bwtsw' is for ref>2G, 'is' for ref<2G).
    bwa index -p ${UREF}/${G2}_snp_upd_genome_BWA -a bwtsw ${UREF}/${G2}_snp_upd_genome.fasta

    echo `date`": building samtools index for ${G2} UPD genome"
    samtools faidx ${UREF}/${G2}_snp_upd_genome.fasta
