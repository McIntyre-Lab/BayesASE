#!/usr/bin/env python3

import argparse
import os
import sys
import numpy as np
import pandas as pd
from functools import reduce

DEBUG = False

##calculate priors and output one file per input comparate (prior_g1, prior_g2, prior_both in the comparate)

def getOptions():
    parser = argparse.ArgumentParser(description='Return best row in blast scores file')
    parser.add_argument("-output", "--output", dest="output", action="store", required=True, help="Output directory for filtered ase counts")
    parser.add_argument("-design", "--design", dest="design", action='store', required=True, help="Design file")
    parser.add_argument("-input", "--input", dest="input", action='store', required=True, help="Path to directory containing summed ase count tables (comparate data file)")
    parser.add_argument("--debug", action='store_true', default=False, help="Print debugging output")

    args=parser.parse_args()
    return(args)

def main():
    """Main Function"""
    args = getOptions()
    global DEBUG
    if args.debug: DEBUG = True

    ## Read in design file as dataframe
    df_design = pd.read_csv(args.design, sep=',', header=0)

#initialize list to store dataframes for each row in design file
    sample_list = []

## Read in design file  (sample = comparate name)
#  G1,G2,sample

## Read input ASE file as df, calculate prior_g1, prior_g2, prior_both and set to separate df
## prior_df FEATURE_ID,prior_${comparate}_g1,prior_${comparate}_g2,prior_${comparate}_both

#iterate over design file
    for index, sample in df_design.iterrows():
        G1 = sample['G1']
        G2 = sample['G2']
        comparate = sample['sample']
        prior_file = comparate + "_prior" 
        print(prior_file)

        ## prior_file = sample['prior_file']
        ## prior_file is the name of the output prior file for the comparate

# read in count table     
        inFile = args.input + '/ase_counts_filtered_' + comparate + '.csv'
        ase_df = pd.read_csv(inFile, index_col=None)

        ##calculate columns for priors calculation

        both_list = [name for name in ase_df.columns if '_both_total_rep' in name]
        g1_list = [name for name in ase_df.columns if '_g1_total_rep' in name]
        g2_list = [name for name in ase_df.columns if '_g2_total_rep' in name]
        total_list = [nameT for nameT in ase_df.columns if '_total_rep' in nameT]

        ase_df['both_counts'] = ase_df.loc[:,both_list].sum(axis=1)
        ase_df['g1_counts'] = ase_df.loc[:,g1_list].sum(axis=1)
        ase_df['g2_counts'] = ase_df.loc[:,g2_list].sum(axis=1)
        ase_df['total_counts'] = ase_df.loc[:,total_list].sum(axis=1)

        ### Set qsim_both as division of both / total, qsim_g1 and qsim_g2 equal to (1 - qsim_both) / 2

        prior_df = pd.DataFrame()
        prior_df['FEATURE_ID'] = ase_df['FEATURE_ID']

        prior_df['prior_' + comparate + '_both'] = ase_df['both_counts'] / ase_df['total_counts']

        prior_df['prior_' + comparate + '_g1'] = np.where(prior_df['prior_' + comparate + '_both'] !=  0, ( 1 - prior_df['prior_' + comparate + '_both']), 0.5 )
        prior_df['prior_' + comparate + '_g2'] = prior_df['prior_' + comparate + '_g1']

        ## Results of this division leave NaN in place of 0, so just fill with 0s
        prior_df['prior_' + comparate + '_both'].fillna(0, inplace=True)
        prior_df['prior_' + comparate + '_g1'].fillna(0, inplace=True)
        prior_df['prior_' + comparate + '_g2'].fillna(0, inplace=True)

        outfilename= prior_file + '.csv' 
        outfile = os.path.join(args.output, outfilename)
        prior_df.to_csv(outfile, index=False)

if __name__=='__main__':
    main()
