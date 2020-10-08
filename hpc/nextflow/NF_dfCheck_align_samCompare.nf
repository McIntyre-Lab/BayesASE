#!/usr/bin/env nextflow

/*
*    Nextflow script
*    to generate report use:  -with-report file-name
*    export _JAVA_OPTIONS=-Djava.io.tmpdir=/ufrc/mcintyre/share/BASE_mclab/ROZ_NF
*/

println """\
    DIRECTORIES AND INPUT FILES
    output alignments:  ${OUTALN}
    samC counts:        ${SAMC}
    scripts:            ${SCRIPTS}
    bedfile:            ${BEDFILE}
    design file:        ${DESIGN_FILE}
    """
    .stripIndent()



DF = Channel.from( DESIGN_FILE )

process checkDF {

    input:
    file DF

    shell:
    '''
    module load python/3.6
    mkdir -p !{CHKS}

    ## DF must have header - check for columns in df and whether FQ file exists in directory
    python !{SCRIPTS}/check_pre_aln_design_10amm.py \
        --design !{DESIGN_FILE} \
        --sampleID sampleID \
        --fqName fqName \
        --g1 G1 \
        --g2 G2 \
        --rep techRep \
        --fqDir !{ORIG}/ \
        --ext fqExtension \
        --readLen readLength \
         --dups !{CHKS}/design_file_list_duplicate_fqNames.csv \
        --logfile !{CHKS}/design_file_check.log
    '''
}



// split design file into 1 row chunks 
// want to execute a task for each row
Channel
    .fromPath( DESIGN_FILE )
    .splitCsv( header: ['G1','G2','SAMPLEID','FQ','EXT','TR','READLEN'], skip: 1 )
    .set { chunks_ch }

process counts {

    input:
    val row from chunks_ch

    output:
    val row into check_ch

    shell:
    '''
    module load bwa/0.7.7 python/2.7 samtools bedtools gcc/5.2.0 bioawk/1.0

    mkdir -p !{ROZ}
    mkdir -p !{CHKALN}
    mkdir -p !{PSAM}
    mkdir -p !{OUTALN}
    mkdir -p !{CHKSC}
    mkdir -p !{SAMC}

    ## set READ and calculate ave readlength
    READ=!{ORIG}/!{row.FQ}!{row.EXT}
    AVE_RL=$(awk '{if(NR%4==2 && length) {count++; bases += length} } END {print bases/count}' ${READ} | awk '{ printf "%.0f\\n", $1 }')
    echo " average RL is:   ${AVE_RL}"

    ## use awk to reorder columms in bed file
    SBED=!{ROZ}/!{row.FQ}_snp_feature_first.bed
    awk -v OFS='\t' '{print $4,$2,$3,$1}' !{BEDFILE} > ${SBED}


    ## (1) Align Reads to Updated Genomes - first to G2 ref then to G1 reference - and Parse sam file
    FQLINEFN=$(wc -l ${READ})
    FQLINE=$(echo ${FQLINEFN} | cut -d" " -f1)
    NUMREAD=$(( FQLINE / 4 ))
    FN=$(echo ${FQLINEFN} | cut -d" " -f2)

    ## count number of starting reads - same for G1 and G2 refs
    echo ${NUMREAD} | awk -v fq=!{row.FQ} -v gq=pre_aln_read_count '{print "filename" "," gq "\\n" fq "," $0}' > !{CHKALN}/pre_aln_reads_!{row.FQ}.csv

    for FOO in G1 G2
    do
        if [[ ${FOO} == 'G1' ]]
        then
            BREF=!{REF}/!{row.G1}_snp_upd_genome_BWA

            echo -e "Aligning !{row.FQ} to !{row.G1}"
            bwa mem -t 8 -M ${BREF} ${READ} > !{OUTALN}/!{row.G1}_!{row.FQ}_upd.sam

            echo -e "Start BWASplitSam on: !{OUTALN}/!{row.G1}_!{row.FQ}_upd.sam"
            !{SCRIPTS}/BWASplitSAM_07mai.py -s !{OUTALN}/!{row.G1}_!{row.FQ}_upd.sam --outdir !{ROZ} -fq1 ${READ}

            ## cat together mapped and opposite
            cat !{ROZ}/!{row.G1}_!{row.FQ}_upd_mapped.sam !{ROZ}/!{row.G1}_!{row.FQ}_upd_oposite.sam > !{PSAM}/!{row.G1}_!{row.FQ}_upd_uniq.sam

        elif [[ ${FOO} == 'G2' ]]
        then
            BREF=!{REF}/!{row.G2}_snp_upd_genome_BWA

            echo -e "Aligning !{row.FQ} to !{row.G2}"
            bwa mem -t 8 -M ${BREF} ${READ} > !{OUTALN}/!{row.G2}_!{row.FQ}_upd.sam

            echo -e "Start BWASplitSam on: !{OUTALN}/!{row.G2}_!{row.FQ}_upd.sam"
            !{SCRIPTS}/BWASplitSAM_07mai.py -s !{OUTALN}/!{row.G2}_!{row.FQ}_upd.sam --outdir !{ROZ} -fq1 ${READ}

            ## cat together mapped and opposite
            cat !{ROZ}/!{row.G2}_!{row.FQ}_upd_mapped.sam !{ROZ}/!{row.G2}_!{row.FQ}_upd_oposite.sam > !{PSAM}/!{row.G2}_!{row.FQ}_upd_uniq.sam
        fi
    done

    ### move alignment summary csv files
    mv !{ROZ}/!{row.G1}_!{row.FQ}_upd_summary.csv !{CHKALN}/!{row.G1}_!{row.FQ}_upd_summary.csv
    mv !{ROZ}/!{row.G2}_!{row.FQ}_upd_summary.csv !{CHKALN}/!{row.G2}_!{row.FQ}_upd_summary.csv


    ## Insert bedtools intersect script + any checks  (reads in aln sam output)
    ###### (2) Bedtools Intersect:   Here we will call the shell script to reformat the sam file so that the have feature names instead of CHR names
    ## In parsed SAM

    for SAMFILE in !{PSAM}/*_!{row.FQ}_upd_uniq.sam
    do
      	MYSAMFILE2=$(basename ${SAMFILE})

        AWKTMP=!{PSAM}/${MYSAMFILE2/_uniq.sam/_uniq_AWK.txt}
        NEWSAM=!{PSAM}/${MYSAMFILE2/_uniq.sam/_uniq_FEATURE.sam}

        #Create a bed file to write the  starting position of every read and an end postion (end = start + readlength)
        awk -v readLen=${AVE_RL} -v OFS='\t' '{print $3,$4,$4+readLen}' ${SAMFILE} > ${AWKTMP}

        BED4=!{PSAM}/${MYSAMFILE2/_uniq.sam/_uniq_int_all.bed}
        BED3=!{PSAM}/${MYSAMFILE2/_uniq.sam/_uniq_int.bed}
        SUM=!{PSAM}/${MYSAMFILE2/_uniq.sam/_drop_summary.csv}

        #Run bedtools intersect with -loj between the reads and the features.
        #We will have one result for each region
        # pipe to awk to remove rows where a read does NOT overlap with a feature
        bedtools intersect -a ${AWKTMP} -b !{BEDFILE} -loj > ${BED4}  

        awk -v OFS='\t' '$4 !="."' ${BED4} > ${BED3}

        ## create file with counts for before and after dropping
        awk -v a=0 -v b=!{row.G2}_!{row.FQ} -v OFS=',' 'BEGIN{print "fqName", "number_overlapping_rows", "total_number_rows"}; { if ($4 !=".") a++} END { print b, a, NR}' ${BED4} > ${SUM}
        rm ${BED4}          

        #With awk substitute column 3 of sam file with column 7 (Feature name) of bed file (using chrom and pos as keys).
        ##omit reads with no feature assigned
        awk -v OFS='\t' 'FNR==NR{a[$1,$2]=$7; next} {$3=a[$3,$4]}1' ${BED3} ${SAMFILE} | awk -F'\t'  '$3!=""' > ${NEWSAM}

        echo "initial sam file ${SAMFILE}"
        echo "awk outfile ${AWKTMP}"
        echo "bed intersect outfile ${BED3}"
        echo "new sam file ${NEWSAM}"

    done

    ## Grab sam files and bed files
        ## sam1 (samA) = G1 and sam2 (samB) = G2
    SAM1=!{PSAM}/!{row.G1}_!{row.FQ}_upd_uniq_FEATURE.sam
    SAM2=!{PSAM}/!{row.G2}_!{row.FQ}_upd_uniq_FEATURE.sam
    BED1=!{PSAM}/!{row.G1}_!{row.FQ}_upd_uniq_int.bed
    BED2=!{PSAM}/!{row.G2}_!{row.FQ}_upd_uniq_int.bed

    awk 'NR==FNR{c[$3]++;next};c[$7] == 0' ${SAM1} ${BED1} > !{CHKSC}/check_sam_bed_!{row.G1}_!{row.FQ}.txt
    awk 'NR==FNR{c[$3]++;next};c[$7] == 0' ${SAM2} ${BED2} > !{CHKSC}/check_sam_bed_!{row.G2}_!{row.FQ}.txt


    ###### (3) Run Sam Compare
    #READ1=!{ORIG}/!{row.FQ}!{row.EXT}

    echo -e "READ1: ${READ}"
    echo -e "SAM1: ${SAM1}"
    echo -e "SAM2: ${SAM2}"
    echo -e "BED:  ${SBED}"
    echo -e "AveRL: ${AVE_RL}"

    echo -e "starting sam compare for:   !{row.FQ}"
    ## NOTE using average read length!!
    python !{SCRIPTS}/sam_compare_w_feature.py \
        -n \
        -l ${AVE_RL} \
        -f ${SBED} \
        -q ${READ} \
        -A ${SAM1} \
        -B ${SAM2} \
        -c !{SAMC}/ase_counts_!{row.FQ}.csv \
        -t !{SAMC}/ase_totals_!{row.FQ}.txt \
        --log !{CHKSC}/ase_log_!{row.FQ}.log

   '''
}

process aln_samC_checks {

    input:
    val row from check_ch

    shell:
    '''  
    module purge
    module load python/3.6

    ### mv drop summary to check_aln dir
    echo "
        Moving drop read summary files to check_aln dir"
    mv !{PSAM}/*_!{row.FQ}_upd_drop_summary.csv !{CHKALN}/

    ### for every FQ file run, should have 2 sam files (NOTE default is SE)
    echo "
	Checking for 2 sam files"
    python !{SCRIPTS}/check_sam_present_04amm.py \
        -fq !{row.FQ} \
        -alnType SE \
        -samPath !{PSAM} \
        -G1 !{row.G1} \
        -G2 !{row.G2} \
        -o !{CHKALN}/check_2_sam_files_!{row.FQ}.txt

    ## run python script to count reads into aln and in each SAM file
    echo "
	Checking for missing reads in sam files"
    python !{SCRIPTS}/check_for_lost_reads_05amm.py \
        -a1 !{CHKALN}/!{row.G1}_!{row.FQ}_upd_summary.csv \
        -a2 !{CHKALN}/!{row.G2}_!{row.FQ}_upd_summary.csv \
        -numread !{CHKALN}/pre_aln_reads_!{row.FQ}.csv \
        -fq !{row.FQ} \
        -o !{CHKALN}/check_start_reads_vs_aln_reads_!{row.FQ}.csv

    echo -e "run sam compare check for !{row.FQ} "
    # Check to make sure counts in csv summary file is within range of minimum unique reads from respective sam files and
    # the summation of the unique reads of both sam files
    python !{SCRIPTS}/check_samcomp_for_lost_reads_03amm.py \
       -b1 !{CHKALN}/!{row.G1}_!{row.FQ}_upd_drop_summary.csv \
       -b2 !{CHKALN}/!{row.G2}_!{row.FQ}_upd_drop_summary.csv \
       -G1 !{row.G1} \
       -G2 !{row.G2} \
       -s !{SAMC}/ase_totals_!{row.FQ}.txt \
       -fq !{row.FQ} \
       -o !{CHKSC}/check_samcomp_!{row.FQ}_aln_2_upd.csv

    '''
}

