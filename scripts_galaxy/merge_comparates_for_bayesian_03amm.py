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
    parser.add_argument("-comp", "--comp", dest="comp", action='store', required=True, help="Input filtered/summarized count tables per one comparate")
    parser.add_argument("-design", "--design", dest="design", action='store', required=True, help="Design file")
    parser.add_argument("-begin", "--begin", dest="begin", action='store', required=False, help="Design file subset beginning(row number)")
    parser.add_argument("-end", "--end", dest="end", action='store', required=False, help="Design file subset end (row number)")
    args=parser.parse_args()
    return(args)

def main():
    args = getOptions()

    ### Read in design file as dataframe
    df_design = pd.read_csv(args.design)

    ### Create subset of design file of comparate specification columns (will quantify # comparates by number of columns left)
    ### Store compID to name output file

    del df_design['G1']
    del df_design['G2']
    del df_design['F1ID']
    
    dict = {}
    col_list = list(df_design.columns.values)
    row_list = []
    comparison_list = df_design['compID'].tolist()
    del df_design['compID']

    ### Create dictionaries per design file row to store the row's comparate files 
    for index, sample in df_design.iterrows():
        dict[index] = list(sample)

    ## If there are comparison columns (column # > 1)
    for key in dict:
        row_list = dict[key]
        file_list = []
        comp_dict = {}
        comparison = comparison_list[key]
        for i, comp in enumerate(row_list):
            comp_dict[i+1] = comp

            ### Assign filename so it can be called
            row_list[i] = args.comp + '/bayesian_input_' + comp + '.csv'

            file = pd.read_csv(row_list[i], index_col=None, header =0)
            file_list.append(file)


        df_merged = reduce(lambda x, y: pd.merge(x, y, on = ['FEATURE_ID','qsim_g1','qsim_g2','qsim_both']), file_list)

        ### drop columns you don't want before merge
        df_merged = df_merged[df_merged.columns.drop(list(df_merged.filter(regex='comp')))]

        df_merged.set_index('FEATURE_ID', inplace=True)

        ### Reassign compID into 'line' column
        df_merged['comparison']= comparison

        merged_headers = list(df_merged.columns.get_values())
        c=[]

        ### For stan model, requires headers to have general comparate input names
        ### This reassigns comparate names to be c1, c2, c3... depending on the order of the comparate subset of the design file (made above)
        for x in comp_dict:
            c= 'c' + str(x)
            for i in range(len(merged_headers)):
                if str(comp_dict[x]) in merged_headers[i]:
                   merged_headers[i] = merged_headers[i].replace(comp_dict[x], c) 
        df_merged.columns=merged_headers




        outfile = args.output + '/bayesian_input_comp_' + comparison + '.csv'
        df_merged.to_csv(outfile)

    ### Need to add subset option to this script (make parallel)
    '''## reindex so pulling 'correct' rows
    begin = int(args.begin) -2
    end = int(args.end) -1
    df_design = df_design[begin:end]
    ##print what subset of the dataframe is being used
    begin = int(args.begin)
    print("begining on row " + str(begin))
    end = int(args.end)
    print("ending on row " + str(end))'''

if __name__=='__main__':
    main()
