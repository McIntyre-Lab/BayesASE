#!/usr/bin/env python

import argparse
import os
import sys
import re
import numpy as np
import pandas as pd
from functools import reduce

DEBUG = False


def getOptions():
    parser = argparse.ArgumentParser(description='Return best row in blast scores file')
    parser.add_argument("-output", "--output", dest="output", action="store", required=True, help="Output directory for filtered ase counts")
    parser.add_argument("-design", "--design", dest="design", action='store', required=True, help="Design file")
    parser.add_argument('-collection_identifiers','--collection_identifiers',dest='collection_identifiers', action='store', required=True, help='Input original names [Required]')
    parser.add_argument('-collection_filenames','--collection_filenames',dest='collection_filenames', action='store', required=True, help='Input galaxy names [Required]')
    parser.add_argument("--debug", action='store_true', default=False, help="Print debugging output")
    args=parser.parse_args()
    return(args)


def main():
    """Main Function"""
    args = getOptions()
    pattern = re.compile(r'(?<=\').*(?=\')')
    identifiers = [pattern.search(i).group() for i in args.collection_identifiers.split(",")]
    filenames = [i.strip() for i in args.collection_filenames.split(",")]
    input_dict = dict(zip(identifiers, filenames))

    global DEBUG
    if args.debug: DEBUG = True

    df_design = pd.read_csv(args.design, sep='\t', header=0)

    sample_list = []

    ## Read in design file  (sample = comparate name)
    #  G1,G2,sample
    ## Read input ASE file as df, calculate prior_g1, prior_g2, prior_both and set to separate df
    ## prior_df FEATURE_ID,prior_${comparate}_g1,prior_${comparate}_g2,prior_${comparate}_both
    #iterate over design file
    #Sample has been changed to comparate
    for index, sample in df_design.iterrows():
        G1 = sample['G1']
        G2 = sample['G2']
        comparate = sample['comparate']
        prior_file = comparate + "_prior"
        print(prior_file)

        ## prior_file = sample['prior_file']
        ## prior_file is the name of the output prior file for the comparate

        inFile = 'ase_counts_filtered_' + comparate
        ase_df = pd.read_csv(input_dict[inFile], index_col=None, sep='\t')
        print(ase_df)

        both_list = [name for name in ase_df.columns if '_both_total_rep' in name]
        g1_list = [name for name in ase_df.columns if '_g1_total_rep' in name]
        g2_list = [name for name in ase_df.columns if '_g2_total_rep' in name]
        total_list = [nameT for nameT in ase_df.columns if '_total_rep' in nameT]

        ase_df['both_counts'] = ase_df.loc[:,both_list].sum(axis=1)
        ase_df['g1_counts'] = ase_df.loc[:,g1_list].sum(axis=1)
        ase_df['g2_counts'] = ase_df.loc[:,g2_list].sum(axis=1)
        ase_df['total_counts'] = ase_df.loc[:,total_list].sum(axis=1)

        prior_df = pd.DataFrame()
        prior_df['FEATURE_ID'] = ase_df['FEATURE_ID']

        prior_df['prior_' + comparate + '_both'] = ase_df['both_counts'] / ase_df['total_counts']
        prior_df['prior_' + comparate + '_g1'] = ase_df['g1_counts'] / ase_df['total_counts']
        prior_df['prior_'+ comparate + '_g2'] = ase_df['g2_counts'] / ase_df['total_counts']

        prior_df['prior_' + comparate + '_both'].fillna(0, inplace=True)
        prior_df['prior_' + comparate + '_g1'].fillna(0, inplace=True)
        prior_df['prior_' + comparate + '_g2'].fillna(0, inplace=True)

        outfilename= prior_file
        outfile = os.path.join(args.output, outfilename)
        prior_df.to_csv(outfile, index=False, sep = '\t')


if __name__=='__main__':
    main()
