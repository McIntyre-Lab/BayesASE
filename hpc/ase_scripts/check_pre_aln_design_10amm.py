#!/usr/bin/env python3

import argparse, csv
import pandas as pd
import os
import sys
import logging
import logging.config

# McLab Packages
import mclib_Python as mclib

#  check that design file contains following headers (in order):
#	G1, G2, sampleID, fqName, fqExtension, techRep, readLength
#       fqName is fastq file without extension

def getOptions():
    parser = argparse.ArgumentParser(description='Check design file.  Design file MUST have following columns: G1, G2, sampleID, fqName, fqExtension, techRep, readLength')
    parser.add_argument('-design','--design',dest='design', action='store', required=True, help='Design file containing fq file names and sample ids [Required]')
    parser.add_argument('-id','--sampleID',dest='sampleID', action='store', required=True, help='Name of the column containing sampleIDs [Required]')
    parser.add_argument('-fq','--fqName',dest='fqName', action='store', required=True, help='Name of the column containing fastq file names [Required]')
    parser.add_argument('-g1','--g1',dest='g1', action='store', required=True, help='Name of the column containing G1 names [Required]')
    parser.add_argument('-g2','--g2',dest='g2', action='store', required=True, help='Name of the column containing G2 names [Required]')
    parser.add_argument('-rep','--rep',dest='rep', action='store', required=True, help='Name of the column containing tech rep identifiers [Required]')
    parser.add_argument('-e','--ext',dest='ext', action='store', required=True, help='fastq extension (ex: .fq, .fastq) [Required]')
    parser.add_argument('-p','--fqDir',dest='fqDir', action='store', required=True, help='Path to the directory containing the fastq files [Required]')
    parser.add_argument('-r','--readLen',dest='readLen', action='store', required=True, help='Name of column containing readLength values [Required]')

    # Output data
    parser.add_argument('-d', '--dups', dest='dups', required=False, help='File containing list of duplicate fqNames in design file')
    parser.add_argument('-l', '--logfile', dest='logfile', required=True, help='Name of log file that checks design file')

    args = parser.parse_args()
    return(args)


#check that names of the fastq files in the design file are unique and that they exist in directory; returns duplicate rows if they exist
def fastq_check(design, fqName, fqDir, ext):

    with open(args.logfile, 'w') as outfile:

        df = pd.read_csv(design)
        if len(df[fqName].unique().tolist()) < len(df[fqName].tolist()):   ##creates lists out of elements in column and compares to a list of unique elements
            dups = df[df.duplicated(fqName, keep=False) == True]           ## creates list of any duplicated rows
            if dups is not None:
                outfile.write('There are duplicate fqNames in your design file!\n')
                with open(args.dups, 'w') as dupout:
                    dups.to_csv(dupout, index=False)
        else:
            outfile.write('No duplicate fqNames in your design file' + '\n')

        count2 = 0
        for i in range(len(df)):                                 ## row by row iteration
            filename = df.iloc[i].loc[fqName]                    ## get filename from column containing filenames
            file = filename + ext                                ## append user-provided extension to filename
            gz = file + '.gz'                                ## create gz variable to check that files do not exist as gz

            if os.path.isfile(os.path.join(fqDir, file)):
                count2 += 1
                continue 
            elif os.path.isfile(os.path.join(fqDir, gz)):
                outfile.write('Error: file ' + gz + ' is zipped. Please unzip your file' + '\n') ##checks if file is zipped (gz) and notifies user
            else:
                outfile.write('File ' + file + ' does not exist in directory ' + fqDir + '\n')
        outfile.write('Number of fq files in design file is ' + str(count2) + '\n')

def columns_check(design, G1, G2, sampleID, fqName, rep, readLen):

    with open(args.logfile, 'a') as outfile:

        df = pd.read_csv(design)
        if G1 not in df:
            outfile.write('Error: column ' + G1 + ' does not exist in design file' + '\n')
        if G2 not in df:
            outfile.write('Error: column ' + G2 + ' does not exist in design file' + '\n')
        if sampleID not in df: 
            outfile.write('Error: column ' + sampleID + ' does not exist in design file' + '\n')
        if fqName not in df:
            outfile.write('Error: column ' + fqName + ' does not exist in design file' + '\n')
        if rep not in df:
            outfile.write('Error: column ' + rep + ' does not exist in design file' + '\n')
        if readLen not in df:
            outfile.write('Error: column ' + readLen + ' does not exist in design file' + '\n')
        columns = ['G1','G2','sampleID','fqName','fqExtension','techRep','readLength']
        headers = list(df)

        if headers != columns:
            outfile.write('ERROR: column headers in file ' + design + ' do not align with order requirements, please check.' + '\n')
        if headers == columns:
            outfile.write('Column headers in file ' + design + ' align with requirements.' + '\n')

##run main
def main(args):

    fastq_check(args.design, args.fqName, args.fqDir, args.ext)

    columns_check(args.design, args.g1, args.g2, args.sampleID, args.fqName, args.rep, args.readLen)

if __name__=='__main__':
    args =  getOptions()
    logging.basicConfig(filename=args.logfile,
        filemode='a',
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.DEBUG)

    main(args)
 

