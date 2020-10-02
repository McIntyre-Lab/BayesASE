#!/usr/bin/env python

import argparse, csv
import pandas as pd
import os
import sys
import logging
import logging.config


def getOptions():
    parser = argparse.ArgumentParser(description='Check design file.  Design file MUST have following columns: G1, G2, sampleID, fqName, fqExtension, techRep, readLength')
    parser.add_argument('-design','--design',dest='design', action='store', required=True, help='Design file containing fq file names and sample ids [Required]')
    parser.add_argument('-id','--sampleID',dest='sampleID', action='store', required=True, help='Name of the column containing sampleIDs [Required]')
    parser.add_argument('-fq','--fqName',dest='fqName', action='store', required=True, help='Name of the column containing fastq file names [Required]')
    parser.add_argument('-g1','--g1',dest='g1', action='store', required=True, help='Name of the column containing G1 names [Required]')
    parser.add_argument('-g2','--g2',dest='g2', action='store', required=True, help='Name of the column containing G2 names [Required]')
    parser.add_argument('-rep','--rep',dest='rep', action='store', required=True, help='Name of the column containing tech rep identifiers [Required]')
    parser.add_argument('-e','--ext',dest='ext', action='store', required=True, help='fastq extension (ex: .fq, .fastq) [Required]')
    parser.add_argument('-r','--readLen',dest='readLen', action='store', required=True, help='Name of column containing readLength values [Required]')
    parser.add_argument('-d', '--dups', dest='dups', required=False, help='File containing list of duplicate fqNames in design file')
    parser.add_argument('-l', '--logfile', dest='logfile', required=True, help='Name of log file that checks design file')

    args = parser.parse_args()
    return(args)


def fastq_check(design, fqName, ext):
    """Check that names of the fastq files in the design file are unique returns duplicate rows if
    they exist
    """
    with open(args.logfile, 'w') as outfile:
        df = pd.read_csv(design, sep='\t', index_col=None)
        print(df)
        # Compare elements in columns to a list of unique elements
        if len(df[fqName].unique().tolist()) < len(df[fqName].tolist()):
            dups = df[df.duplicated(fqName, keep=False) == True]
            if dups is not None:
                outfile.write('There are duplicate fqNames in your design file!\n')
                with open(args.dups, 'w') as dupout:
                    dups.to_csv(dupout, index=False)
        else:
            outfile.write('No duplicate fqNames in your design file' + '\n')


def columns_check(design, G1, G2, sampleID, fqName, rep, readLen):
    columns = ['G1','G2','sampleID','fqName','fqExtension','techRep','readLength']
    with open(args.logfile, 'a') as outfile:
        df = pd.read_csv(design, sep='\t', index_col=None)
        headers = list(df)
        if G1 not in df:
            outfile.write('Error: {} column does not exist in design file\n'.format(G1))
        if G2 not in df:
            outfile.write('Error: {} column does not exist in design file\n'.format(G2))
        if sampleID not in df:
            outfile.write('Error: {} column does not exist in design file\n'.format(sampleID))
        if fqName not in df:
            outfile.write('Error: {} column does not exist in design file\n'.format(fqName))
        if rep not in df:
            outfile.write('Error: {} column does not exist in design file\n'.format(rep))
        if readLen not in df:
            outfile.write('Error: {} column called does not exist in design file\n'.format(readLen))
        if headers != columns:
            outfile.write('ERROR: column headers in {} do not align with order requirements\n'.format(design))
        if headers == columns:
            outfile.write('Column headers in {} align with order requirements\n'.format(design))


def main():
    args = getOptions()
    logging.basicConfig(filename=args.logfile,
        filemode='a',
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.DEBUG)
    fastq_check(args.design, args.fqName, args.ext)
    #  check that design file contains following headers (in order):
    #	G1, G2, sampleID, fqName, fqExtension, techRep, readLength
    #       fqName is fastq file without extension
    columns_check(args.design, args.g1, args.g2, args.sampleID, args.fqName, args.rep, args.readLen)


if __name__=='__main__':
    main()

