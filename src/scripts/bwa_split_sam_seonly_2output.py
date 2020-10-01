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
    parser = argparse.ArgumentParser(description="Takes a SE aligned SAM file and split into different categories")

    tool = parser.add_argument_group(title='Tool Specific Inputs')
    tool.add_argument("-s", "--sam", dest="sam", action='store', required=True, help="Name of the SAM file [required]")
    tool.add_argument("-summname", "--summname", dest="summname", action='store', required=False, help="Name in the summary file")

    output = parser.add_argument_group(description="Output")
    output.add_argument("--uniq", dest="uniq", action="store", required=True, help="mapped reads file")
    output.add_argument("--summ", dest="summ",  action="store", required=True, help="summary file")
    args=parser.parse_args()
    
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

def SplitSAMSE (sam,summname):
    """Function to split all the reads in PE SAM files"""

    # Setting flags
    flags_uniq         = ["0","16"]
    flags_chimeric       = ["2048","2064"]
    flags_unmappedreads  = ["4"]
    flags_notprimary     = ["256","272"]

    # Setting counters
    counter_total         = 0
    counter_mapped        = 0
    counter_oppositestrand = 0
    counter_ambiguous     = 0
    counter_chimeric      = 0
    counter_unmappedread  = 0
    counter_notprimary    = 0

    # Lists for mapped and ambiguous reads
    unmappedread = []
    ambiguous    = []

    # Filename
    bname = os.path.basename(sam)
    name  = os.path.splitext(bname)[0]

    # Open SAM file and output files in SAM format.
    SAM        = open(sam,'r')
    UNIQ     = open(args.uniq, 'w')
    # Open Sumary file
    SUMMARY    = open(args.summ, 'w')

    # Reading line by line SAM file (except headers)
    for line in SAM:
        if line.startswith('@'):continue
        elements = line.strip().split("\t")

        # Getting unmapped reads
        if elements[1] in flags_unmappedreads:
            unmappedread.append(elements[0])
            counter_total        += 1
            counter_unmappedread += 1
        # Getting & printing "CHIMERIC" reads
        elif elements[1] in flags_chimeric:
            counter_total    += 1
            counter_chimeric += 1
        # Getting & printing "NOT PRIMARY" reads
        elif elements[1] in flags_notprimary:
            counter_total    += 1
            counter_notprimary += 1
        # Getting & printing AMBIGUOUS reads, those who are not ambiguous are 
        # store as mapped reads
        elif elements[1] in flags_uniq:
            if(elements[1]=="0"):
                regmatch=re.match(".+\tAS:i:([0-9]+)\tXS:i:([0-9]+).*", line)
                if int(regmatch.group(1))-int(regmatch.group(2))==0:
                    ambiguous.append(elements[0])
                    counter_total     += 1
                    counter_ambiguous += 1
                else:
                    print('\t'.join(elements), file=UNIQ)
                    counter_total  += 1
                    counter_mapped += 1
            else:
                print('\t'.join(elements), file=UNIQ)
                counter_total         += 1
                counter_oppositestrand += 1

        #If not in the previous categories then unknown
        else:
            print("Warning: "+elements[1]+" key is not recognized")

    #Print summary
    count_names = ["name",
                    "count_total_reads",
                    "count_mapped_read_opposite_strand",
                    "count_unmapped_read",
                    "count_mapped_read",
                    "count_ambiguous_read",
                    "count_chimeric_read",
                    "count_notprimary"] 
    count_values = [summname,
                    counter_total,
                    counter_oppositestrand,
                    counter_unmappedread,
                    counter_mapped,
                    counter_ambiguous,
                    counter_chimeric,
                    counter_notprimary]

    count_values = list(map(str,count_values))
    print('\t'.join(count_names), file=SUMMARY)
    print('\t'.join(count_values), file=SUMMARY)

    #Clossing all files
    SAM.close()
    UNIQ.close()
    SUMMARY.close()

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

    # Split SAM FILE for Single End
    unmapped,ambiguous = SplitSAMSE(args.sam, summname)

    # If FastQ provided then output unmmaped and ambiguous reads as FQ else finish

if __name__=='__main__':
    # Setting parser
    args = getOptions()

    # Starting script
    main(args)
