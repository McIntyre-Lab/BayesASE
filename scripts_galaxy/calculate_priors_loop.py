##this version contains added checks for missing qsim values


#!/usr/bin/env python3

import argparse
import os
import sys
import numpy as np
import pandas as pd
from functools import reduce

DEBUG = False

## calculate priors and output one file of counts containing stacked rowsfor all g1/g2 pairs
## for features with no reads - output .......

def getOptions():
    parser = argparse.ArgumentParser(description='Return best row in blast scores file')
    parser.add_argument("-o", "--output", dest="output", action="store", required=True, help="Output directory for filtered ase counts")
    parser.add_argument("-g1", "--g1", dest="g1", action='store', required=True, help="column with G1 values")
    parser.add_argument("-g2", "--g2", dest="g2", action='store', required=True, help="column with G2 values")
    parser.add_argument("-s", "--sam-compare-dir", dest="samCompDir", action='store', required=True, help="Path to directory containing summed ase count tables")
    parser.add_argument("--debug", action='store_true', default=False, help="Print debugging output")

    args=parser.parse_args()
    return(args)

def main():
    """Main Function"""
    args = getOptions()
    global DEBUG
    if args.debug: DEBUG = True


    #initialize list to store dataframes for each row in design file
    sample_list = []

    G1 = args.g1
    print(G1)
    G2 = args.g2.strip()

    print(G2)
    F1ID = G2 + '_' + G1
    outfilename= 'priors_' + F1ID + '.csv' 
    print(outfilename + " out1")
    outfile = os.path.join(args.output, outfilename)
    count_missing_file = 0

    # read in count table     
    inFile = 'ase_sum_sim_counts_' + F1ID + '.csv'
    print(inFile + " infile1")
    samC = os.path.join(args.samCompDir, inFile)
    try:
        samFile = pd.read_csv(samC, sep=',', header=0) 
    except:
        print(f"Missing:\n {samC}")
        count_missing_file += 1
        sys.exit(1)

    ## add columns for g1 and g2 to dataframe
    samFile['g1'] = G1
    samFile['g2'] = G2

    ##calculate columns for priors calculation
    samFile['both_total'] = samFile['BOTH_EXACT'] + samFile['BOTH_INEXACT_EQUAL']
    samFile['g2_total'] = samFile['SAM_A_ONLY_EXACT'] + samFile['SAM_A_ONLY_SINGLE_INEXACT'] + samFile['SAM_A_EXACT_SAM_B_INEXACT'] + samFile['SAM_A_INEXACT_BETTER'] 
    samFile['g1_total'] = samFile['SAM_B_ONLY_EXACT'] + samFile['SAM_B_ONLY_SINGLE_INEXACT'] + samFile['SAM_B_EXACT_SAM_A_INEXACT'] + samFile['SAM_B_INEXACT_BETTER']
    samFile['ase_total'] = samFile['g1_total'] + samFile['g2_total'] + samFile['both_total']

    ## calculate priors
    samFile['qsim_g1'] = samFile['g1_total'] / samFile['ase_total']
    samFile['qsim_g2'] = samFile['g2_total'] / samFile['ase_total']
    samFile['qsim_both'] = samFile['both_total'] / samFile['ase_total']


    ## if <= 0 then make qsim 0.5
    samFile['qsim_g1'] = np.where(samFile.qsim_g1 <= 0, 0.5, samFile.qsim_g1)
    samFile['qsim_g2'] = np.where(samFile.qsim_g2 <= 0, 0.5, samFile.qsim_g2)


    ##check for missing qsim values (empty)
    for row, value in samFile.iterrows():
        if samFile.iloc[row].loc['qsim_g1'] is None or samFile.iloc[row].loc['qsim_g2'] is None or samFile.iloc[row].loc['qsim_both'] is None:
            print('ERROR: missing qsim value for FEATURE_ID ' + samFile.iloc[row].loc['FEATURE_ID']	+ ' in file ' +	inFile)
        
    #subset desired columns
    sam_subset = samFile[['FEATURE_ID','g1', 'g2','qsim_g1', 'qsim_g2', 'qsim_both']]
    del samFile ##clean up
        
    #add dataframe to df_dict 
    sample_list.append(sam_subset)
#    print(sample_list)
    
    #stack dataframes stored in dict
    df_out = pd.concat(sample_list)
    print(df_out)

    #write out file
    df_out.to_csv(outfile, index=False)
if __name__=='__main__':
    main()
