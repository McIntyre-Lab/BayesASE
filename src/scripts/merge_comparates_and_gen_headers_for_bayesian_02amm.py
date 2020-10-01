#!/usr/bin/env python3

import re
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
#    parser.add_argument("-comp", "--comp", dest="comp", action='store', required=True, help="Input filtered/summarized count tables per one comparate")
    parser.add_argument('-collection_identifiers','--collection_identifiers',dest='collection_identifiers', action='store', required=True, help="ASE count table collection identifiers") 
    parser.add_argument('-collection_filenames','--collection_filenames',dest='collection_filenames', action='store', required=True, help="ASE count table collection filenames")
    parser.add_argument("-design", "--design", dest="design", action='store', required=True, help="Design file")
    args=parser.parse_args()
    return(args)

def main():
    args = getOptions()

#Modify to allow Galaxy to take input as a collection

    pattern = re.compile(r'(?<=\').*(?=\')')    
    identifiers = [pattern.search(i).group() for i in args.collection_identifiers.split(",")]
    filenames = [i.strip() for i in args.collection_filenames.split(",")]
    input_dict_comp = dict(zip(identifiers, filenames))


    ### Read in design file as dataframe
    #Make sure design file is read as a tsv
#    df_design = pd.read_csv(args.design)
    df_design = pd.read_csv(args.design, sep ='\t')

    ### Create subset of design file of comparate specification columns (will quantify # comparates by number of columns left)
    ### Store compID to name output file

    c1_g1_list = df_design['C1_G1'].tolist()
    c1_g2_list = df_design['C1_G2'].tolist()
    c2_g1_list = df_design['C2_G1'].tolist()
    c2_g2_list = df_design['C2_G2'].tolist()
    c1_list = df_design['Comparate_1'].tolist()
    c2_list = df_design['Comparate_2'].tolist()

    del df_design['C1_G1']
    del df_design['C1_G2']
    del df_design['C2_G1']
    del df_design['C2_G2']

#Changed dict to dict_b since "dict" is name already used above to read collections     
    dict_b = {}
    col_list = list(df_design.columns.values)
    row_list = []
    comparison_list = df_design['compID'].tolist()
    del df_design['compID']

    ### Create dictionaries per design file row to store the row's comparate files 
    for index, sample in df_design.iterrows():
        dict_b[index] = list(sample)

    ## If there are comparison columns (column # > 1)
    for key in dict_b:
        row_list = dict_b[key]
        file_list = []
        comp_dict = {}
        comparison = comparison_list[key]
        c1_g1= c1_g1_list[key]
        c1_g2= c1_g2_list[key]
        c2_g1= c2_g1_list[key]
        c2_g2= c2_g2_list[key]
        c1= c1_list[key]
        c2= c2_list[key]
        for i, comp in enumerate(row_list):
            comp_dict[i+1] = comp

            ### Assign filename so it can be called
            # Keep file names that Galaxy assigns so that Galaxy can recognize the collection
            # Also removed extension since last script (merge with prior does not contain extension
#            row_list[i] = args.comp + '/bayesian_input_' + comp + '.csv'

            identifier = 'bayesian_input_' + comp
            row_list[i] = input_dict_comp[identifier]

#Change pd.read_csv to pd.read_table to read file into dataframe
#            file = pd.read_csv(row_list[i], index_col=None, header=0)

            file = pd.read_table(row_list[i], index_col=None, header=0)
            file_list.append(file)


        df_merged = reduce(lambda x, y: pd.merge(x, y, on = ['FEATURE_ID']), file_list)

        ### drop columns you don't want before merge
        df_merged = df_merged[df_merged.columns.drop(list(df_merged.filter(regex='comp')))]

        df_merged.set_index('FEATURE_ID', inplace=True)

        ## AMM fixing below line get_values is deprecated
        ## merged_headers = list(df_merged.columns.get_values())
        merged_headers = list(df_merged.columns.to_numpy())

        ### For stan model, requires headers to have general comparate input names
        ### This reassigns comparate names to be c1, c2, c3... depending on design file specifications
        for x in comp_dict:
            for i in range(len(merged_headers)):
                if c1 in merged_headers[i]:
                   merged_headers[i] = merged_headers[i].replace(c1, 'c1') 
                if c2 in merged_headers[i]:
                   merged_headers[i] = merged_headers[i].replace(c2, 'c2') 

        df_merged.columns=merged_headers


        df_filtered = df_merged

#Output file in TSV format, and without an extension so that next script knows what name to expect 
#        outfile = args.output + '/bayesian_input_' + comparison + '.csv'
        outfile = args.output + '/bayesian_input_' + comparison
        df_filtered.to_csv(outfile, sep='\t')

if __name__=='__main__':
    main()
