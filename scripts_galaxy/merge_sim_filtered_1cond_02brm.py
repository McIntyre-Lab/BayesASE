#!/usr/bin/env python3

import argparse
import os
import sys
import pandas as pd
import numpy as np

DEBUG = False

## merge simulation counts with filtered ase counts to create file for Bayesian input

def getOptions():
    parser = argparse.ArgumentParser(description='Return best row in blast scores file')
    parser.add_argument("-o", "--output", dest="output", action="store", required=True, help="Output directory for merged  ase counts")
    parser.add_argument("-cf", "--countsf", dest="countsf", action='store', required=True, help="ase filtered counts file")
    parser.add_argument("-comp", "--comp", dest="comp", action='store', required=True, help="Comparate1 column")
    parser.add_argument("-sf", "--sf", dest="sf", action='store', required=True, help="simulated counts file")
    parser.add_argument("-g1", "--g1", dest="g1", action='store', required=True, help="Genome one")
    parser.add_argument("-g2", "--g2", dest="g2", action='store', required=True, help="Genome two")
    parser.add_argument("--debug", action='store_true', default=False, help="Print debugging output")
    args=parser.parse_args()
    return(args)

def main():
    """Main Function"""
    args = getOptions()
    global DEBUG
    if args.debug: DEBUG = True

    comp = str(args.comp)
    g1 = str(args.g1)
    g2 = str(args.g2)

    ## Read in ase_filtered counts file and sim counts file as dataframes
    comp2 = comp.rsplit('_', 1)[0]
    filtered_file = "ase_counts_filtered_" + comp2 + ".csv"
    simulated_file = 'priors_' + g2 + '_' + g1 + ".csv"
    
    print(filtered_file)
    df_filtered = pd.read_csv(os.path.join(args.countsf, filtered_file))
    df_filtered = df_filtered.reset_index(drop=True)
    print(df_filtered.columns)
    df_sim = pd.read_csv(os.path.join(args.sf, simulated_file))
    df_sim = df_sim.reset_index(drop=True)

##Add column checks!!

    ## merge filtered counts with sim counts - merge by FEATURE_ID, g1, and g2 columns
    df_merged = pd.merge(df_filtered,df_sim, on= ['FEATURE_ID','g1','g2'], how='inner')
    print('df_merged')
    print(df_merged.columns)
    del df_merged['g1']
    del df_merged['g2']
    cols_to_order=['FEATURE_ID','qsim_g1','qsim_g2','qsim_both', comp2 + '_flag_analyze', comp2 + '_num_reps']
    new_columns = df_merged.columns.drop(cols_to_order)
    print(new_columns)



    new_df_merged = pd.DataFrame()
    new_df_merged['FEATURE_ID']=df_merged['FEATURE_ID']
    new_df_merged['qsim_g1']=df_merged['qsim_g1']
    new_df_merged['qsim_g2']=df_merged['qsim_g2']
    new_df_merged['qsim_both']=df_merged['qsim_both']
    new_df_merged[comp2 + '_flag_analyze']=df_merged[comp2 + '_flag_analyze']
    new_df_merged[comp2 + '_num_reps']=df_merged[comp2 + '_num_reps']
    print('hi')
    print(new_df_merged.columns)
    new_df_merged[new_columns] = df_merged[new_columns]
    
    new_df_merged = new_df_merged[new_df_merged.columns.drop(list(new_df_merged.filter(regex='apn')))]

    new_df_merged['comp']=comp2
    print(new_df_merged.columns)

## Need to change qsim column names to include arguments g1 g2..

    ##write out file
#    newID= g2 + '_' + g1
    outfilename = "bayesian_input_" + comp2 + ".csv"
    outfile = os.path.join(args.output, outfilename)
    new_df_merged.to_csv(outfile, index=False)


    if DEBUG:
        print(f"Output file:\n{outfile}")

if __name__=='__main__':
    main()
