#!/bin/sh
#SBATCH --mail-user=yourname@your.email
#SBATCH --job-name=aln_upd
#SBATCH --account=mcintyre
#SBATCH --qos=mcintyre-b
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o example_out/logs/aln_upd.%A-%a.out
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=8
#SBATCH --mem=50gb
#SBATCH --array=2-25


# aligns each fq file to both updated references
# runs sam compare script
## note design file has header so start on array=2


# Load modules
module load bwa/0.7.7
module load python/2.7.6
module load bedtools/2.27.1
module load samtools/1.9
module load htslib


## Set / Create Directories and Variables
#Everything is relative to current directory
SCRIPTS=hpc/ase_scripts
REF=example_out/reference/updated_genomes_vcfConsensus
ORIG=example_in/reads

BEDFILE=example_in/reformatted_BASE_testdata_bedfile.bed

## Create output directory for alignments to updated genome
OUTALN=example_out/aln_upd_genome
    if [ ! -e $OUTALN ]; then mkdir -p $OUTALN; fi
PSAM=example_out/aln_upd_genome_bwa_parse
    if [ ! -e $PSAM ]; then mkdir -p $PSAM; fi

## Create output directory for ase counts from sam compare
SAMC=example_out/ase_counts_updated
    if [ ! -e $SAMC ]; then mkdir -p $SAMC; fi

## Create output directory for upd aln summaries and checks
CHKALN=example_out/check_aln
    if [ ! -e $CHKALN ]; then mkdir -p $CHKALN; fi

## Create output directory for Sam Compare check
CHKSC=example_out/check_samcomp
    if [ ! -e $CHKSC ]; then mkdir -p $CHKSC; fi

DESIGN_FILE=example_in/df_BASE_galaxy_W55_noEmptyFq.csv
DESIGN=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $DESIGN_FILE)
IFS=',' read -ra ARRAY <<< "$DESIGN"

G1=${ARRAY[0]}
G2=${ARRAY[1]}
READLEN=${ARRAY[5]}
FQ=${ARRAY[3]}
EXT=${ARRAY[4]}

## Create temp dir
ROZ=roz_${FQ}
    mkdir -p ${ROZ}

## set READ and calculate ave readlength
READ=${ORIG}/${FQ}${EXT}
echo " read is $READ 
"

AVE_RL=$(awk '{if(NR%4==2 && length) {count++; bases += length} } END {print bases/count}' ${READ} | awk '{ printf "%.0f\\n", $1 }')

######  Create modified BED file to use in SAM compare - this bed has features 1st with start and end positions in genome
## use awk to reorder columms in bed file
SBED=example_out/snp_feature_first.bed

echo "Reformatting $BEDFILE"
awk -v OFS='\t' '{print $4,$2,$3,$1}' $BEDFILE > $SBED


###### (1) Align Reads to Updated Genomes - first to G2 ref then to G1 reference - and Parse sam file
FQLINEFN=$(wc -l $READ)
FQLINE=$(echo $FQLINEFN | cut -d" " -f1)
NUMREAD=$(( FQLINE / 4 )) 
FN=$(echo $FQLINEFN | cut -d" " -f2)
    
## count number of starting reads - same for G1 and G2 refs
echo $NUMREAD | awk -v fq=${FQ} -v gq=pre_aln_read_count '{print "filename" "," gq "\n" fq "," $0}' > $CHKALN/pre_aln_reads_${FQ}.csv



for FOO in G1 G2
do
    if [[ $FOO == 'G2' ]]
    then
        BREF=$REF/${G2}_snp_upd_genome_BWA

        echo "Aligning G2 to reference $BREF"
		bwa mem -t 8 -M $BREF $READ > $OUTALN/${G2}_${FQ}_upd.sam

        echo -e "Start BWASplitSam on: $OUTALN/${G2}_${FQ}_upd.sam"
        $SCRIPTS/BWASplitSAM_07mai.py -s $OUTALN/${G2}_${FQ}_upd.sam --outdir $ROZ -fq1 $READ
 
        ## cat together mapped and opposite
        cat $ROZ/${G2}_${FQ}_upd_mapped.sam $ROZ/${G2}_${FQ}_upd_oposite.sam > $PSAM/${G2}_${FQ}_upd_uniq.sam

    elif [[ $FOO == 'G1' ]]
    then
        BREF=$REF/${G1}_snp_upd_genome_BWA

        echo "Aligning G1 to reference $BREF"
        bwa mem -t 8 -M $BREF $READ > $OUTALN/${G1}_${FQ}_upd.sam

        echo -e "Start BWASplitSam on: $OUTALN/${G1}_${FQ}_upd.sam"
        $SCRIPTS/BWASplitSAM_07mai.py -s $OUTALN/${G1}_${FQ}_upd.sam --outdir $ROZ -fq1 $READ

        ## cat together mapped and opposite
        cat $ROZ/${G1}_${FQ}_upd_mapped.sam $ROZ/${G1}_${FQ}_upd_oposite.sam > $PSAM/${G1}_${FQ}_upd_uniq.sam
    fi
done

### move alignment summary csv files
mv ${ROZ}/${G1}_${FQ}_upd_summary.csv ${CHKALN}/${G1}_${FQ}_upd_summary.csv
mv ${ROZ}/${G2}_${FQ}_upd_summary.csv ${CHKALN}/${G2}_${FQ}_upd_summary.csv

### for every FQ file run, should have 2 sam files (NOTE default is SE)
echo "
    checking for 2 sam files"
    
python $SCRIPTS/check_sam_present_04amm.py \
    -fq $FQ \
    -alnType SE \
    -samPath $PSAM \
    -G1 $G1 \
    -G2 $G2 \
    -o $CHKALN/check_2_sam_files_${FQ}.txt

## run python script to count reads into aln and in each SAM file
echo "
    checking for missing reads in sam files"

python $SCRIPTS/check_for_lost_reads_05amm.py \
    -a1 $CHKALN/${G1}_${FQ}_upd_summary.csv \
    -a2 $CHKALN/${G2}_${FQ}_upd_summary.csv \
    -numread $CHKALN/pre_aln_reads_${FQ}.csv \
    -fq $FQ \
    -o $CHKALN/check_start_reads_vs_aln_reads_${FQ}.csv


## Insert bedtools intersect script + any checks  (reads in aln sam output)
###### (2) Bedtools Intersect:   Here we will call the shell script to reformat the sam file so that the have feature names instead of CHR names
## In parsed SAM, 

for SAMFILE in $PSAM/*_${FQ}_upd_uniq.sam
do
    MYSAMFILE2=$(basename $SAMFILE)

    AWKTMP=$PSAM/${MYSAMFILE2/_uniq.sam/_uniq_AWK.txt}
    NEWSAM=$PSAM/${MYSAMFILE2/_uniq.sam/_uniq_FEATURE.sam}    

    #Create a bed file to write the  starting position of every read and an end postion (end = start + readlength)
    awk -v readLen=${READLEN} -v OFS='\t' '{print $3,$4,$4+readLen}' $SAMFILE > $AWKTMP

    BED4=${PSAM}/${MYSAMFILE2/_uniq.sam/_uniq_int_all.bed}
    BED3=$PSAM/${MYSAMFILE2/_uniq.sam/_uniq_int.bed}
    SUM=${PSAM}/${MYSAMFILE2/_uniq.sam/_drop_summary.txt}

    #Run bedtools intersect with -loj between the reads and the features. 
    #We will have one result for each region 
    # pipe to awk to remove rows where a read does NOT overlap with a feature
    bedtools intersect -a $AWKTMP -b $SBED -loj > ${BED4}

    awk -v OFS='\t' '$4 !="."' ${BED4} > $BED3
    
    ## create file with counts for before and after dropping
    awk -v a=0 -v b=${G2}_${FQ} -v OFS=',' 'BEGIN{print "fqName", "number_overlapping_rows", "total_number_rows"delimited}; { if ($4 !=".") a++} END { print b, a, NR}' ${BED4} > ${SUM}

    #With awk substitute column 3 of sam file with column 7 (Feature name) of bed file (using chrom and pos as keys).
    ##omit reads with no feature assigned
    awk -v OFS='\t' 'FNR==NR{a[$1,$2]=$7; next} {$3=a[$3,$4]}1' ${BED3} $SAMFILE | awk -F'\t'  '$3!=""' > $NEWSAM 

    echo initial sam file $SAMFILE 
    echo awk outfile $AWKTMP
    echo bed intersect outfile $BED3
    echo new sam file "$NEWSAM"

done 

       

## Grab sam files and bed files
	## sam1 (samA) = G1 and sam2 (samB) = G2
SAM1=$PSAM/${G1}_${FQ}_upd_uniq_FEATURE.sam
SAM2=$PSAM/${G2}_${FQ}_upd_uniq_FEATURE.sam
BED1=$PSAM/${G1}_${FQ}_upd_uniq_int.bed
BED2=$PSAM/${G2}_${FQ}_upd_uniq_int.bed

awk 'NR==FNR{c[$3]++;next};c[$7] == 0' $SAM1 $BED1 > $CHKSC/check_sam_bed_${G1}_${FQ}.txt
awk 'NR==FNR{c[$3]++;next};c[$7] == 0' $SAM2 $BED2 > $CHKSC/check_sam_bed_${G2}_${FQ}.txt

###### (3) Run Sam Compare

READ1=${ORIG}/${FQ}${EXT}

echo -e "READ1: '${READ1}"
echo -e "SAM1: '${SAM1}'"
echo -e "SAM2: '${SAM2}'"
echo -e "BED: '${SBED}'"

echo -e "starting sam compare for $FQ "
## NOTE using average read length!!
python $SCRIPTS/sam_compare_w_feature.py \
    -n \
    -l ${AVE_RL} \
    -f $BEDFILE \
    -q $READ1 \
    -A $SAM1 \
    -B $SAM2 \
    -c $SAMC/ase_counts_${FQ}.csv \
    -t $SAMC/ase_totals_${FQ}.txt \
    --log $CHKSC/ase_log_${FQ}.log

### mv drop summary to check_aln dir
echo "
    Moving drop read summary files to check_aln dir"
mv ${PSAM}/*_${FQ}_upd_drop_summary.txt ${CHKALN}/

echo -e "run sam compare check for $FQ "
# Check to make sure counts in csv summary file is within range of minimum unique reads from respective sam files and 
# the summation of the unique reads of both sam files
python $SCRIPTS/check_samcomp_for_lost_reads_03amm.py \
    -b1 $CHKALN/${G1}_${FQ}_upd_drop_summary.txt \
    -b2 $CHKALN/${G2}_${FQ}_upd_drop_summary.txt \
    -G1 $G1 \
    -G2 $G2 \
    -s $SAMC/ase_totals_${FQ}.txt \
    -fq $FQ \
    -o $CHKSC/check_samcomp_${FQ}_aln_2_upd.csv

rm -r $ROZ


