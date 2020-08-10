#!/bin/sh
#SBATCH --mail-user=breccam@ufl.edu
#SBATCH --job-name=aln_upd
#SBATCH --account=mcintyre
#SBATCH --qos=mcintyre-b
#SBATCH --mail-type=FAIL
#SBATCH --no-requeue
#SBATCH -o /ufrc/mcintyre/share/BASE_mclab/galaxy/test_scripts/SLURM_LOGS/aln_upd.%A-%a.out
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=8
#SBATCH --mem=20gb
#SBATCH --array=1-12


# aligns to updated references using bash loop across design file
# runs sam compare script

# Load modules
module load bwa/0.7.7
module load python/2.7.6
module load bedtools/2.27.1
module load samtools/1.9
module load htslib


## Set / Create Directories and Variables
PROJ=/ufrc/mcintyre/share/BASE_mclab/galaxy
PY=$PROJ/scripts/ase_scripts
UPD=$PROJ/updated_genomes_vcfConsensus
ORIG=$PROJ/output_test_fq

BEDFILE=$PROJ/test_input/BASE_testData_galaxy_100bp.bed


## Create output directory for alignments to updated genome
OUTALN=$PROJ/aln_upd_genome
    mkdir -p $OUTALN
PSAM=${PROJ}/aln_upd_genome_bwa_parse
SAMC=${PROJ}/ase_counts_updated
CHKS="${PROJ}/ase_check_summaries
CHKALN=${PROJ}/check_aln
CHKSC=${PROJ}/check_samcomp
ROZ=${PROJ}/roz_test


DESIGN_FILE=${PROJ}/design_files/df_BASE_galaxy_test_data_W55_noEmptyFq.csv
DESIGN=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $DESIGN_FILE)
IFS=',' read -ra ARRAY <<< "$DESIGN"

G1=${ARRAY[0]}
G2=${ARRAY[1]}
READLEN=${ARRAY[6]}
FQ=${ARRAY[3]}
EXT=${ARRAY[4]}

## create temp directory 
ROZ=${ROZ_TMP}/roz_${FQ}
    mkdir -p $ROZ

    SBED=$ROZ/snp_feature_first.bed

    ## set READ and calculate ave readlength
    READ=$ORIG/${FQ}${EXT}
    AVE_RL=$(awk '{if(NR%4==2 && length) {count++; bases += length} } END {print bases/count}' ${READ} | awk '{ printf "%.0f\\n", $1 }')

    ######  Create modified BED file to use in SAM compare - this bed has features 1st with start and end positions in genome
    ## use awk to reorder columms in bed file
    echo "
        Reformatting $BEDFILE"
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

            echo -e "Aligning ${FQ} to ${G2}"
            bwa mem -t 8 -M $BREF $READ > $OUTALN/${G2}_${FQ}_upd.sam

            echo -e "Start BWASplitSam on: $OUTALN/${G2}_${FQ}_upd_CG10932.sam"
            $SCRIPTS/BWASplitSAM_07mai.py -s $OUTALN/${G2}_${FQ}_upd_CG10932.sam --outdir $ROZ -fq1 $READ
 
            ## cat together mapped and opposite
            cat $ROZ/${G2}_${FQ}_upd_CG10932_mapped.sam $ROZ/${G2}_${FQ}_upd_CG10932_oposite.sam > $PSAM/${G2}_${FQ}_upd_CG10932_uniq.sam

        elif [[ $FOO == 'G1' ]]
        then
            BREF=$REF/${G1}_snp_upd_genome_BWA

            echo -e "Aligning ${FQ} to ${G1}"
            bwa mem -t 8 -M $BREF $READ > $OUTALN/${G1}_${FQ}_upd.sam

            echo -e "Start BWASplitSam on: $OUTALN/${G1}_${FQ}_upd_CG10932.sam"
            $SCRIPTS/BWASplitSAM_07mai.py -s $OUTALN/${G1}_${FQ}_upd_CG10932.sam --outdir $ROZ -fq1 $READ

            ## cat together mapped and opposite
            cat $ROZ/${G1}_${FQ}_upd_CG10932_mapped.sam $ROZ/${G1}_${FQ}_upd_CG10932_oposite.sam > $PSAM/${G1}_${FQ}_upd_CG10932_uniq.sam
        fi
    done




    ## Insert bedtools intersect script + any checks  (reads in aln sam output)
    ###### (2) Bedtools Intersect:   Here we will call the shell script to reformat the sam file so that the have feature names instead of CHR names
    ## In parsed SAM, 

    for SAMFILE in $PSAM/*_${FQ}_upd_CG10932_uniq.sam
    do
        MYSAMFILE2=$(basename $SAMFILE)

        AWKTMP=$PSAM/${MYSAMFILE2/_uniq.sam/_uniq_AWK.txt}
        NEWSAM=$PSAM/${MYSAMFILE2/_uniq.sam/_uniq_FEATURE.sam}    

        #Create a bed file to write the  starting position of every read and an end postion (end = start + readlength)
        awk -v readLen=${READLEN} -v OFS='\t' '{print $3,$4,$4+readLen}' $SAMFILE > $AWKTMP

        BED3=$PSAM/${MYSAMFILE2/_uniq.sam/_uniq_int.bed}

        #Run bedtools intersect with -loj between the reads and the features. 
        #We will have one result for each region 
        # pipe to awk to remove rows where a read does NOT overlap with a feature
        bedtools intersect -a $AWKTMP -b $BEDFILE -loj |  awk -v OFS='\t' '$4 !="."' > $BED3
    
        #With awk substitute column 3 of sam file with column 7 (Feature name) of bed file (using chrom and pos as keys).
        ##omit reads with no feature assigned
        awk -v OFS='\t' 'FNR==NR{a[$1,$2]=$7; next} {$3=a[$3,$4]}1' ${BED3} $SAMFILE | awk -F'\t'  '$3!=""' > $NEWSAM 

        echo initial sam file $SAMFILE 
        echo awk outfile $AWKTMP
        echo bed intersect outfile $BED3
        echo new sam file "$NEWSAM"

    done 

