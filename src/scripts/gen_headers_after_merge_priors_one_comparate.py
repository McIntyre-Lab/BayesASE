#!/usr/bin/env python3

import re
import argparse
import os
import sys
import numpy as np
from functools import reduce
from collections import OrderedDict
import pandas as pd

DEBUG = False

def getOptions():
    parser = argparse.ArgumentParser(
        description='Create headers for model for a for a single comparate.'
    )
    parser.add_argument(
        "-output",
        "--output",
        dest="output",
        action="store",
        required=True,
        help="Output directory for complete merged comparate files ready for Bayesian"
    )
    parser.add_argument(
        "-collection_identifiers",
        "--collection_identifiers",
        dest="collection_identifiers",
        action="store",
        required=True,
        help="ASE count table collection identifiers"
    )
    parser.add_argument(
        "-collection_filenames",
        "--collection_filenames",
        dest="collection_filenames",
        action='store',
        required=True,
        help="ASE count table collection filenames"
    )
    parser.add_argument(
        "-design",
        "--design",
        dest="design",
        action='store',
        required=True,
        help="Design file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Print debugging output"
    )
    args = parser.parse_args()
    return args

def main():
    args = getOptions()
    global DEBUG
    if args.debug:
        DEBUG=True

    identifiers = [i.strip() for i in args.collection_identifiers.split(",")]
    filenames = [i.strip() for i in args.collection_filenames.split(",")]
    input_dict_comp = dict(zip(identifiers, filenames))
    if DEBUG:
        print(f"DEBUG: input dict:\n{input_dict_comp}")

    ### Read in design file as dataframe
    #Make sure design file is read as a tsv
    df_design = pd.read_csv(args.design, sep ='\t')
    if DEBUG:
        print(f"DEBUG: design:\n{df_design}")

    ### Subset design file and create comparate specification columns 
    ### Store compID to name output file
    c1_list = df_design['Comparate_1'].tolist()

    #Changed dict to dict_b since "dict" is name already used above to read collections  
    sample_dict = {}
    #col_list = list(df_design.columns.values)
    row_list = []
    comparison_list = df_design['compID'].tolist()
    del df_design['compID']

    ### Create dictionaries per design file row to store the row's comparate files 
    for index, sample in df_design.iterrows():
        sample_dict[index] = list(sample)

    ## Create a dictionary containing the comparisons between each parental genome the comparate
    for key in sample_dict:
        row_list = sample_dict[key]
        file_list = []
        comp_dict = {}
        comparison = comparison_list[key]
        c1 = c1_list[key]
        for i, comp in enumerate(row_list):
            comp_dict[i + 1] = comp

            # Assign filename so that Galaxy can correctly call and recognize the collection
            comp_name = 'bayesian_input_' + comp
            row_list[i] = input_dict_comp[comp_name]

            #Use pd.read_table to read file into dataframe
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
        ### This reassigns comparate names to be c1
        for x in comp_dict:
            for i in range(len(merged_headers)):
                if c1 in merged_headers[i]:
                   merged_headers[i] = merged_headers[i].replace(c1, 'c1')

        df_merged.columns=merged_headers

        df_filtered = df_merged

        #Change the output name from bayesian_input_comp to bayesian_input

        outfile = args.output + '/bayesian_input_' + comparison
        df_filtered.to_csv(outfile, sep='\t')


if __name__=='__main__':
    main()
