#!/usr/bin/env python3

import argparse
import os
import sys
import numpy as np
from functools import reduce
from collections import OrderedDict
import pandas as pd

## merge filtered/summarized files with qsim values by user-specified comparison

def getOptions():
    parser = argparse.ArgumentParser(description='Merges together filtered/summarized comparate count tables by user-specified comparison')
    parser.add_argument("-output", "--output", dest="output", action="store", required=True, help="Output directory for complete merged comparate files ready for Bayesian")
    parser.add_argument("-comp", "--comp", dest="comp", action='store', required=True, help="Directory to input filtered/summarized count tables per one comparate")
    parser.add_argument("-design", "--design", dest="design", action='store', required=True, help="Design file")
    parser.add_argument("-prior", "--prior", dest="prior", action='store', required=False, help="Directory to input prior files if given")
    args=parser.parse_args()
    return(args)

def main():
    args = getOptions()

    ### Read in design file as dataframe
    df_design = pd.read_csv(args.design)
    
    ## add column for prior file name
    sample = df_design['sample']
    p_file = sample + "_prior"
    df_design['prior_file'] = p_file
#    print(df_design)

    dict = {}
    col_list = list(df_design.columns.values)
    row_list = []

    g1_list = df_design['G1'].tolist()
    g2_list = df_design['G2'].tolist()
    comparate_list = df_design['sample'].tolist()
    prior_list = df_design['prior_file'].tolist()

#    print(prior_list) 

    ### Create dictionaries per design file row to store the row's comparate files 
    for index, sample in df_design.iterrows():
        dict[index] = list(sample)
        
    ## If there are comparison columns (column # > 1)
    for key in dict:
        row_list = dict[key]
        file_list = []
        comp_dict = {}

        g1 = g1_list[key]
        g2 = g2_list[key]
        comparate = comparate_list[key]
        prior_file = prior_list[key]

        data_fileName = args.comp + '/ase_counts_filtered_' + comparate + '.csv'
        data_df = pd.read_csv(data_fileName, index_col=None, header =0)

        prior_fileName = args.prior + '/' + comparate + '_prior.csv'
        print(prior_fileName)
        prior_df = pd.read_csv(prior_fileName, index_col=None, header =0)

#        print(data_df['FEATURE_ID'])
#        print(prior_df['FEATURE_ID'])

        ## CHECK: make sure that the feautre_id columns of the prior file and the comparate data file are exactly the same
        diff_features = data_df['FEATURE_ID'].equals(prior_df['FEATURE_ID'])
#        print(diff_features)
        ## If feature_id columns are the same, merge priors into data file
        if diff_features == True:

            del data_df['FEATURE_ID']
            del data_df['g1']
            del data_df['g2']

            merge_list = []
            merge_list.append(prior_df)
            merge_list.append(data_df)
            df_merged = pd.concat(merge_list, axis=1)

#            print(df_merged)
            outfileName = args.output + '/bayesian_input_' + comparate + '.csv'
            df_merged.to_csv(outfileName, index=False)

            ## Results of this division might leave NaN in place of 0, so just fill with 0
            df_merged['prior_' + comparate + '_both'].fillna(0, inplace=True)
            df_merged['prior_' + comparate + '_g1'].fillna(0, inplace=True)
            df_merged['prior_' + comparate + '_g2'].fillna(0, inplace=True)

            ### For features where all qsim values = 0, make sure flag analyze equals 0!! Will tank Bayesian if not
            prior_list = [nameq for nameq in df_merged.columns if 'prior' in nameq]
            df_merged['prior_sum'] = df_merged.loc[:,prior_list].sum(axis=1)
            df_merged.loc[df_merged['prior_sum'] == 0, comparate + '_flag_analyze'] = 0

            ### Add in other check to make sure g1 and g2 counts aren't both 0 - will crash otherwise!!!
            x_list = [namex for namex in df_merged.columns if '_g1_total_rep' in namex]
            y_list = [namey for namey in df_merged.columns if '_g2_total_rep' in namey]
            df_merged['X'] = df_merged.loc[:,x_list].sum(axis=1)
            df_merged['Y'] = df_merged.loc[:,y_list].sum(axis=1)
            df_merged['g1_g2_sum'] = df_merged['X'] + df_merged['Y']
            df_merged.loc[df_merged['g1_g2_sum'] == 0, comparate + '_flag_analyze'] = 0


            ### Delete columns not needed downstream
            del df_merged['prior_sum']
            del df_merged['X']
            del df_merged['Y']
            del df_merged['g1_g2_sum']


        else:
            feature_diff_error = 'Comparate data file FEATURE_IDs and those in the prior file must be the same and in the same order'
            outfileName = args.output + '/check_features' + comparate + '.csv'
            print(feature_diff_error, file=outfileName)
            sys.exit()

if __name__=='__main__':
    main()
