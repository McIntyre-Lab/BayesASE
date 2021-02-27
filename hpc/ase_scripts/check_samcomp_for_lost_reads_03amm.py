#!/usr/bin/env python
import csv, sys, argparse, os, itertools, operator, collections
import pandas as pd
import numpy as np
csv.field_size_limit(1000000000)

### check read numbers into and out of sam compare
### outputs a file 


# Parse command line arguments
parser = argparse.ArgumentParser(description='check read numbers into and out of sam compare, must be within minimum unique reads and sum of uniq reads from both summary files')
parser.add_argument('-b1','--bwa1',dest='bwa1', action='store', required=True, help='The sam G1 summary file after dropping non-overlapping reads [Required]')
parser.add_argument('-G1','--G1',dest='G1', action='store', required=True, help='The genotype all others are compared to [Required]')
parser.add_argument('-b2','--bwa2',dest='bwa2', action='store', required=True, help='The sam G2 summary file after dropping non-overlapping reads [Required]')
parser.add_argument('-G2','--G2',dest='G2', action='store', required=True, help='comparing genotype [Required]')
parser.add_argument('-fq','--fq',dest='fq', action='store', required=True, help='fastq filename [Required]')
parser.add_argument('-s','--sam',dest='sam',action='store',required=True, help='The ase totals file containing read counts used in sam compare [Required]')
parser.add_argument('-o','--out', dest='out', action='store', required=True, help='Output file containing check info [Required]')
args = parser.parse_args()
  

       
### Open bwa
with open(args.bwa1,'r') as bwa_table:
    B1 = csv.reader(bwa_table, delimiter= ',')
    next(B1)
    for row in B1:
        uniq_b1 = int(row[1])
        ## total reads after dropping

with open(args.bwa2, 'r') as bwa2_table:
    B2 = csv.reader(bwa2_table, delimiter= ',')
    next(B2)
    for row in B2:
        uniq_b2 = int(row[1])
        ## total reads after dropping

## read # in sam file should be between greater of uniq_b1 or uniq_b2 - this should be the same # as in the ase_totals table
sumReads=uniq_b1 + uniq_b2
minReads=min(uniq_b1, uniq_b2)
print(sumReads)
print(minReads)
with open(args.sam, 'r') as sam_table:
    df = pd.read_csv(sam_table, sep='\t')
    print(df)
#    headerIdx = [index for index, row in enumerate(sam_table) if row.startswith('@')]
#    df = pd.read_table(sam_table,header=None,usecols=[0,1,2], skiprows=headerIdx[0:])

    count_tot=df['Count totals:'].iloc[len(df)-1]
    print(count_tot)

if minReads <= count_tot <= sumReads:
    flag_readnum_in_range = 1
else:
    flag_readnum_in_range = 0

## counts in sam file should be betweeen minReads and the sum of uniq mapped reads 
## open file to write to
with open(args.out, 'w') as outfile:
    spamwriter=csv.writer(outfile, delimiter=',')
    first_row = True
    
    if first_row: 
        spamwriter.writerow(['fqName', 'min_uniq_g1_uniq_g2', 'sum_uniq_g1_uniq_g2', 'total_counts_ase_table', 'flag_readnum_in_range'])
        first_row = False

        row_items = [args.fq, minReads, sumReads, count_tot, flag_readnum_in_range]
    spamwriter.writerow(row_items)

