#!/usr/bin/env python3

import csv, sys, argparse, os, itertools, operator, collections, logging
import logging.config
import pandas as pd
import numpy as np
import re

##Check that user's Pre-Bayesian design file adheres to BASE requirements
##Make sure that the headers are in the correct order and file is properly formatted 

parser = argparse.ArgumentParser(description='Check user-supplied Pre-Bayesian design file for correct formatting and adherence to BASE guidelines ')
parser.add_argument('-design','--design',dest='design', action='store', required=True, help='Input Design File. See BASE User Guide for formatting help [REQUIRED]')
parser.add_argument('-compNum','--compNum',dest='compNum',type=int, action='store', required=True, help='Number of comparates')

# output file
parser.add_argument('-o','--out', dest='out', action='store', required=True, help='Name of log file that checks design file')
args = parser.parse_args()
 
#Check that columns G1, G2, comparate_1, and compID exist in design file (and in that order!)

#Make a list of the headers in the design file

headers= []
df=pd.read_csv(args.design, sep='\t', index_col=None)
list(df)
headers=df.columns.tolist()

#Make sure name of Design file is in output file
in_file = os.path.split(args.design)[1]

#Generate list of fixed header names 
g1='C1_G1'
g2='C1_G2'
c1='C2_G1'
c2='C2_G2'
comparate_1='Comparate_1'
comparate_2='Comparate_2'
compID='compID'
    
#Generate list of correct header order by comparate        
fixed_header_comp1=[g1,g2,comparate_1,compID]
fixed_header_comp2=[g1,g2,c1,c2,comparate_1,comparate_2,compID]



#Check that user labeled columns correctly

with open(args.out, 'w') as outfile:

    first_row = True

    if first_row:
        outfile.write('Design_file' + '\t' + 'message\n')
        first_row = False

    if args.compNum==1:
        if headers!=fixed_header_comp1:
            outfile.write(in_file + '\t'+ 'Error: Format of design file does not align with BASE requirements' + '\n' + '\t' + 'Column names are either incorrectly labeled, missing, or out of order')
        else:
            outfile.write(in_file + '\t' + 'The columns are labeled correctly and in correct order'+ '\n')
    #If there are two comparates 
    elif args.compNum==2:
        if headers!=fixed_header_comp2:
            outfile.write(in_file + '\t'+ 'Error: Format of design file does not align with BASE requirements' + '\n' +'\t' + 'Column names are either incorrectly labeled, missing, or out of order' + '\n')
        else:
            outfile.write(in_file + '\t' + 'The columns are labeled correctly and in correct order'+ '\n' + '\t'+ 'Continue with Bayesian Analysis')

#Tell user what headers are incorrectly labeled or missing 

with open(args.out, 'a') as outfile:
    
    if args.compNum==1 and headers!=fixed_header_comp1:
        if g1 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + g1 + ' does not exist or is mislabeled in design file' + '\n')
        if g2 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + g2 + ' does not exist or is mislabeled in design file' + '\n')
        if comparate_1 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + comparate_1 + ' does not exist or is mislabeled in design file' + '\n')
        if compID not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + compID + ' does not exist or is mislabeled in design file' + '\n')
    elif args.compNum==2 and headers!=fixed_header_comp2:
        if g1 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + g1 + ' does not exist or is mislabeled in design file' + '\n')
        if g2 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + g2 + ' does not exist or is mislabeled in design file' + '\n')
        if c1 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + c1 + ' does not exist or is mislabeled in design file' + '\n')
        if c2 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + c2 + ' does not exist or is mislabeled in design file' + '\n')
        if comparate_1 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + comparate_1 + ' does not exist or is mislabeled in design file' + '\n')
        if comparate_2 not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + comparate_2 + ' does not exist or is mislabeled in design file' + '\n')
        if compID not in headers:
            outfile.write('\n' + '\t' + 'Error: column called ' + compID + ' does not exist or is mislabeled in design file' + '\n')


