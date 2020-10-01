#!/usr/bin/env python3

import argparse
import os
import sys
import numpy as np
from functools import reduce
from collections import OrderedDict
import pandas as pd
import re

## merge filtered/summarized files with qsim values by user-specified comparison

def getOptions():
    parser = argparse.ArgumentParser(description='Merges together filtered/summarized comparate count tables by user-specified comparison')
    #parser.add_argument("-output", "--output", dest="output", action="store", required=True, help="Output directory for complete merged comparate files ready for Bayesian")
    #parser.add_argument("-comp", "--comp", dest="comp", action='store', required=True, help="Directory to input filtered/summarized count tables per one comparate")
    parser.add_argument("-design", "--design", dest="design", action='store', required=True, help="Design file")
    #parser.add_argument("-prior", "--prior", dest="prior", action='store', required=False, help="Directory to input prior files if given")
    parser.add_argument('-collection1_identifiers','--collection1_identifiers',dest='collection1_identifiers', action='store', required=True, help="ASE count table collection identifiers") 
    parser.add_argument('-collection1_filenames','--collection1_filenames',dest='collection1_filenames', action='store', required=True, help="ASE count table collection filenames")
    parser.add_argument('-collection2_identifiers','--collection2_identifiers',dest='collection2_identifiers', action='store', required=True, help="Prior count table collection identifiers")
    parser.add_argument('-collection2_filenames','--collection2_filenames',dest='collection2_filenames', action='store', required=True, help="ASE count table collection filenames")
    parser.add_argument('-out','--out', dest='out', action='store', required=True, help='Output directory for complete merged comparate files ready for Bayesian')
    args=parser.parse_args()
    return(args)

def main():
    args = getOptions()
    pattern = re.compile(r'(?<=\').*(?=\')')
    
    identifiers_ASE = [pattern.search(i).group() for i in args.collection1_identifiers.split(",")]
    filenames_ASE = [i.strip() for i in args.collection1_filenames.split(",")]
    input_dict_ASE = dict(zip(identifiers_ASE, filenames_ASE))
    
    identifiers_priors = [pattern.search(i).group() for i in args.collection2_identifiers.split(",")]
    filenames_priors = [i.strip() for i in args.collection2_filenames.split(",")]
    input_dict_priors = dict(zip(identifiers_priors, filenames_priors))
    
    ### Read in design file as dataframe
    df_design = pd.read_csv(args.design,sep='\t')
    
    ## add column for prior file name
    #Sample column has been changed to comparate
    sample = df_design['comparate']
    p_file = sample + "_prior"
    df_design['prior_file'] = p_file
#    print(df_design)

    dict_new = {}
    col_list = list(df_design.columns.values)
    row_list = []

    g1_list = df_design['G1'].tolist()
    g2_list = df_design['G2'].tolist()
    comparate_list = df_design['comparate'].tolist()
    prior_list = df_design['prior_file'].tolist()

#    print(prior_list) 

    ### Create dictionaries per design file row to store the row's comparate files 
    for index, sample in df_design.iterrows():
        dict_new[index] = list(sample)
        
    ## If there are comparison columns (column # > 1)
    for key in dict_new:
        row_list = dict_new[key]
        file_list = []
        comp_dict = {}

        g1 = g1_list[key]
        g2 = g2_list[key]
        comparate = comparate_list[key]
        prior_file = prior_list[key]

        data_fileName = 'ase_counts_filtered_' + comparate
        data_df = pd.read_csv(input_dict_ASE[data_fileName], index_col=None, header =0, sep='\t')

        prior_fileName = comparate + '_prior'
        #print(prior_fileName)
        prior_df = pd.read_csv(input_dict_priors[prior_fileName], index_col=None, header =0, sep='\t')

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
            outfileName = args.out + '/bayesian_input_' + comparate
            df_merged.to_csv(outfileName, index=False, sep ='\t')

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
            outfileName = args.out + '/check_features' + comparate + '.csv'
            print(feature_diff_error, file=outfileName)
            sys.exit()

if __name__=='__main__':
    main()
