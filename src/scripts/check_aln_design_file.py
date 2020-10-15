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
    parser.add_argument('-design_identifier','--design_identifier',dest='design_identifier', action='store', required=True, help='Design file identifier [Required]')
    parser.add_argument('-d', '--dups', dest='dups', required=False, help='File containing list of duplicate fqNames in design file')
    parser.add_argument('-l', '--logfile', dest='logfile', required=True, help='Name of log file that checks design file')
    args = parser.parse_args()
    return(args)


def fastq_check(design):
    fqName = 'fqName'
    with open(args.dups, 'w') as outfile:
        df = pd.read_csv(design, sep='\t', index_col=None)
        if len(df[fqName].unique().tolist()) < len(df[fqName].tolist()):
            dups = df[df.duplicated(fqName, keep=False) == True]
            if dups is not None:
                outfile.write('Duplicate check:\tThere are duplicate fqNames in your design file!')
                outfile.write(f'\t{'-'*33}')
                outfile.write('Duplicated Rows:\n')
                dups.to_csv(outfile, index=False, sep="\t")
                return -1
        else:
            outfile.write('Duplicate check:\tNo duplicate fqNames in your design file\t\n')
            return 0

def columns_check(design, design_identifier):
    columns = ['G1','G2','sampleID','fqName','fqExtension','techRep','readLength']
    with open(args.logfile, 'w') as outfile:
        df = pd.read_csv(design, sep='\t', index_col=None)
        headers = list(df)
        if headers != columns:
            outfile.write(f"""Headers check:\tERROR: column headers in file {design_identifier}
 do not align with order requirements, please check.\n{'-'*33}
Details:\n""")
            for col in columns:
                if col not in df:
                    outfile.write(f'\tError: column header {col} does not exist in design file.')
            return -1
        if headers == columns:
            outfile.write(f'Header check:\tColumns in {design_identifier} align with requirements.')
            return 0


def main():
    args = getOptions()
    col_match = columns_check(args.design, args.design_identifier)
    logging.basicConfig(filename=args.logfile,
        filemode='a',
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.DEBUG)
    fastq_check(args.design, args.fqName, args.ext)
    if_dup = fastq_check(args.design)


if __name__=='__main__':
    main()

