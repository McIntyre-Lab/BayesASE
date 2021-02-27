#!/usr/bin/env python
#Standar Libraries
import os
import re
import logging
import argparse
import numpy as np

#AddOn Libraries
from Bio.SeqIO.QualityIO import FastqGeneralIterator

def getOptions():
    """Function to pull in arguments"""
    parser = argparse.ArgumentParser(description="Takes a SAM file [either SE"\
            " or PE] and splits its reads into different categories")
    parser.add_argument("-s", dest="sam", action='store', required=True, 
                        help="Name of the SAM file [required]")
    parser.add_argument("-fq1", dest="fq1", action='store', required=False, 
                        help="Name of the FastQ1 file [required]")
    parser.add_argument("-fq2", dest="fq2", action='store', required=False, 
                        default=False, help="Name of the FastQ2 file")
    parser.add_argument("-summname", dest="summname", action='store', 
                        required=False, help="Name in the summary file")
    parser.add_argument("--outdir", dest="odir" , action='store', 
                        required=True, help="Out directory path")
    args=parser.parse_args()

    # Standardized some paths before continue
    if args.fq1:
        args.fq1  = os.path.abspath(args.fq1)
    if args.fq2:
        args.fq2  = os.path.abspath(args.fq2)
    args.sam  = os.path.abspath(args.sam)
    args.odir = os.path.abspath(args.odir)

    return (args)

def readFastQ(fastq_path):
    """
    Reads fastq file and returns a dictionary with the header as a key
    """
    with open(fastq_path,'r') as FASTQ:
        fastq_generator = FastqGeneralIterator(FASTQ)
        readDict = {re.sub('/[1-2]','',header).split(' ')[0]:(seq,qual) for header,
                    seq,qual in fastq_generator}

    return (readDict)

def writeOutput (headList,readDict,out_path):
    """
    Reads a list of headers and a dictionary to output a fastq file format
    with the reads of those headers.
    """
    with open(out_path,"w") as OUTFILE:
        for head in headList:
            OUTFILE.write ('\n'.join(['@'+head,readDict[head][0],'+',
                            readDict[head][1],'']))

def SplitSAMPE (fname,odir,summname):
    """Function to split all the reads in PE SAM files"""
    
    #Setting flags
    flags_bothunmapped1 = ["77"]
    flags_bothunmapped2 = ["141"]
    flags_unmappedread1 = ["69","101","177"]
    flags_unmappedread2 = ["133","165","181"]
    flags_opositestrand = ["81","97","145","161"]
    flags_mapped1       = ["65","73","83","89","99","113","121"]
    flags_mapped2       = ["153","185","137","147","163","129","117"]
    flags_grayones      = ["321","323","329","337","339","353","355","369",
                           "371","377","385","387","393","401","403","417",
                           "419","433","435","441"]

    #Setting counters
    total                 = 0
    counter_mapped1       = 0
    counter_mapped2       = 0
    counter_grayones      = 0
    counter_ambiguous1    = 0
    counter_ambiguous2    = 0
    counter_unmappedread1 = 0
    counter_unmappedread2 = 0
    counter_bothunmapped1 = 0
    counter_bothunmapped2 = 0
    counter_opositestrand = 0

    #Lists for unmapped and ambiguous reads
    ambiguous1    = []
    ambiguous2    = []
    unmappedread1 = []
    unmappedread2 = []
    bothunmapped1 = []
    bothunmapped2 = []

    #Filename
    bname = os.path.basename(fname)
    name  = os.path.splitext(bname)[0]

    #Open SAM file and output files in SAM format.
    SAM          = open(fname,'r')
    GRAY         = open(os.path.join(odir,name+'_gray.sam'),'w')
    MAPPED       = open(os.path.join(odir,name+'_mapped.sam'),'w')
    OPOSITE      = open(os.path.join(odir,name+'_oposite.sam'),'w')
    AMBIGUOUS    = open(os.path.join(odir,name+'_ambiguous.sam'),'w')
    UNRECOGNIZED = open(os.path.join(odir,name+'_unrecognized.sam'),'w')

    #Open Sumary file
    SUMMARY      = open(os.path.join(odir,name+'_summary.csv'),'w')

    #Reading line by line SAM file (except headers)
    for line in SAM:
        if line.startswith('@'):continue
        elements=line.strip().split('\t')

        #Getting unmapped reads
        if elements[1] in flags_unmappedread1:
            unmappedread1.append(elements[0])
            counter_unmappedread1 += 1
            total += 1
        elif elements[1] in flags_unmappedread2:
            unmappedread2.append(elements[0])
            counter_unmappedread2 += 1
            total += 1
        elif elements[1] in flags_bothunmapped1:
            bothunmapped1.append(elements[0])
            counter_bothunmapped1 += 1
            total += 1  
        elif elements[1] in flags_bothunmapped2:
            bothunmapped2.append(elements[0])
            counter_bothunmapped2 += 1  
            total += 1

        # Getting & printing "gray" reads
        elif elements[1] in flags_grayones:
            print >> GRAY,'\t'.join(elements)
            counter_grayones += 1
            total += 1
        # Getting & printing "OPOSITE" reads
        elif elements[1] in flags_opositestrand:
            print >> OPOSITE,'\t'.join(elements)
            counter_opositestrand += 1
            total += 1

        # Getting & printing AMBIGUOUS reads, those who are not ambiguous 
        # are store as mapped reads
        elif elements[1] in flags_mapped1:
            regmatch=re.match(".+\tAS:i:([0-9]+)\tXS:i:([0-9]+).*",line)
            if int(regmatch.group(1))-int(regmatch.group(2))==0:
                print >> AMBIGUOUS,'\t'.join(elements)
                ambiguous1.append(elements[0])
                counter_ambiguous1 += 1
                total += 1
            else:
                print >> MAPPED,'\t'.join(elements)
                counter_mapped1 += 1
                total += 1

        elif elements[1] in flags_mapped2:
            regmatch=re.match(".+\tAS:i:([0-9]+)\tXS:i:([0-9]+).*",line)
            if int(regmatch.group(1))-int(regmatch.group(2))==0:
                print >> AMBIGUOUS,'\t'.join(elements)
                ambiguous2.append(elements[0])
                counter_ambiguous2 += 1
                total += 1
            else:
                print >> MAPPED,'\t'.join(elements)
                counter_mapped2 += 1
                total += 1

        # If not in the previous categories then unknown
        else:
            print "Warning: "+elements[1]+" key is not recognized"
            print >> UNRECOGNIZED,'\t'.join(elements)
            

    # Print summary
    count_names = ["name","total_reads","counter_oposite_strand_read",
                    "counter_grayones","counter_unmapped_read1",
                    "counter_unmapped_read2","counter_both_unmapped_read1",
                    "counter_both_unmapped_read2","counter_mapped_read1",
                    "counter_mapped_read2","counter_ambiguous_read1",
                    "counter_ambiguous_read2"] 
    count_values = [summname,total,counter_opositestrand,
                    counter_grayones,counter_unmappedread1,
                    counter_unmappedread2,counter_bothunmapped1,
                    counter_bothunmapped2,counter_mapped1,
                    counter_mapped2,counter_ambiguous1,
                    counter_ambiguous2]
    count_values = map(str,count_values)
    print >> SUMMARY,','.join(count_names)
    print >> SUMMARY,','.join(count_values)


    # Clossing all files
    SAM.close()
    GRAY.close()
    MAPPED.close()
    SUMMARY.close()
    OPOSITE.close()
    AMBIGUOUS.close()
    UNRECOGNIZED.close()
    
        
    #return(unmappedread1,unmappedread2)
    return(unmappedread1,unmappedread2,
            bothunmapped1,bothunmapped2,
            ambiguous1,ambiguous2)

def SplitSAMSE (sam,odir,summname):
    """Function to split all the reads in PE SAM files"""

    # Setting flags
    flags_mapped        = ["0"]
    flags_chimeric      = ["2048","2064"]
    flags_unmappedreads = ["4"]
    flags_opositestrand = ["16"]
    
    # Setting counters
    counter_total         = 0
    counter_mapped        = 0
    counter_ambiguous     = 0
    counter_chimeric      = 0
    counter_unmappedread  = 0
    counter_opositestrand = 0

    # Lists for mapped and ambiguous reads
    unmappedread = []
    ambiguous    = []

    # Filename
    bname = os.path.basename(sam)
    name  = os.path.splitext(bname)[0]

    # Open SAM file and output files in SAM format.
    SAM       = open(sam,'r')
    MAPPED    = open(os.path.join(odir,name+'_mapped.sam'),'w')
    OPOSITE   = open(os.path.join(odir,name+'_oposite.sam'),'w')
    CHIMERIC  = open(os.path.join(odir,name+"_chimeric.sam"),"w")
    AMBIGUOUS = open(os.path.join(odir,name+'_ambiguous.sam'),'w')

    # Open Sumary file
    SUMMARY   = open(os.path.join(odir,name+'_summary.csv'),'w')

    # Reading line by line SAM file (except headers)
    for line in SAM:
        if line.startswith('@'):continue
        elements = line.strip().split("\t")

        # Getting unmapped reads
        if elements[1] in flags_unmappedreads:
            unmappedread.append(elements[0])
            counter_total        += 1
            counter_unmappedread += 1
        # Getting & printing "OPOSITE" reads
        elif elements[1] in flags_opositestrand:
            print >> OPOSITE,'\t'.join(elements)
            counter_total         += 1
            counter_opositestrand += 1
        # Getting & printing "CHIMERIC" reads
        elif elements[1] in flags_chimeric:
            print >> CHIMERIC,"\t".join(elements)
            counter_total    += 1
            counter_chimeric += 1
        # Getting & printing AMBIGUOUS reads, those who are not ambiguous are 
        # store as mapped reads
        elif elements[1] in flags_mapped:
            regmatch=re.match(".+\tAS:i:([0-9]+)\tXS:i:([0-9]+).*",line)
            if int(regmatch.group(1))-int(regmatch.group(2))==0:
                print >> AMBIGUOUS,'\t'.join(elements)
                ambiguous.append(elements[0])
                counter_total     += 1
                counter_ambiguous += 1
            else:
                print >> MAPPED,'\t'.join(elements)
                counter_total  += 1
                counter_mapped += 1

        #If not in the previous categories then unknown
        else:
            print "Warning: "+elements[1]+" key is not recognized"


    #Print summary
    count_names = ["name",
                    "count_total_reads",
                    "count_mapped_read_oposite_strand",
                    "count_unmapped_read",
                    "count_mapped_read",
                    "count_ambiguous_read",
                    "count_chimeric_read"] 
    count_values = [summname,
                    counter_total,
                    counter_opositestrand,
                    counter_unmappedread,
                    counter_mapped,
                    counter_ambiguous,
                    counter_chimeric]

    count_values = map(str,count_values)
    print >> SUMMARY  ,','.join(count_names)
    print >> SUMMARY  ,','.join(count_values)

    #Clossing all files
    SAM.close()
    MAPPED.close()
    SUMMARY  .close()
    OPOSITE.close()
    CHIMERIC.close()
    AMBIGUOUS.close()
    
    #return(unmappedread1,unmappedread2)
    return(unmappedread,ambiguous)

def main(args):
    """Here we call all other functions"""

    # Paths
    bname = os.path.basename(args.sam)
    name  = os.path.splitext(bname)[0]

    if not args.summname:
        summname = name
    else:
        summname = args.summname

    if args.fq2:
        # If FastQ provided then output unmmaped and ambigous reads as FQ
        # For Paired End reads
        unmapped1,unmapped2,bothunmapped1,bothunmapped2,ambiguous1,ambiguous2 = SplitSAMPE(args.sam,args.odir,summname)
            
        # Print unMapped1, bothinmapped1 and ambiguous1
        fastQ1Dict = readFastQ(args.fq1)
        writeOutput (unmapped1,fastQ1Dict,os.path.join(args.odir, name + '_unmapped1.fq'))
        writeOutput (ambiguous1,fastQ1Dict,os.path.join(args.odir, name + '_ambiguous1.fq'))
        writeOutput (bothunmapped1, fastQ1Dict, os.path.join(args.odir, name + '_both_unmapped1.fq'))
        del fastQ1Dict

        #Print unMapped1, bothinmapped2 and ambiguous2
        fastQ2Dict = readFastQ(args.fq2)
        writeOutput (unmapped2,fastQ2Dict,os.path.join(args.odir, name + '_unmapped2.fq'))
        writeOutput (ambiguous2,fastQ2Dict,os.path.join(args.odir, name + '_ambiguous2.fq'))
        writeOutput (bothunmapped2, fastQ2Dict, os.path.join(args.odir, name + '_both_unmapped2.fq'))
        del fastQ2Dict


    else:
        # Split SAM FILE for Single End
        unmapped,ambiguous = SplitSAMSE(args.sam,args.odir,summname)

        # If FastQ provided then output unmmaped and ambiguous reads as FQ else finish
        if args.fq1:
            # Crreate dictionary with FastQ (if any)
            fastQDict = readFastQ(args.fq1)
            writeOutput (unmapped,fastQDict,os.path.join(args.odir, name + '_unmapped.fq'))
            writeOutput (ambiguous,fastQDict,os.path.join(args.odir, name + '_ambiguous.fq'))


if __name__=='__main__':
    # Setting parser
    args = getOptions()

    # Starting script
    main(args)