#!/usr/bin/env python
import csv, sys, argparse, os, itertools, operator, collections
import pandas as pd
import numpy as np
from csv import DictReader
csv.field_size_limit(1000000000)

### check read numbers into and out of sam compare
### outputs a file 


# Parse command line arguments
parser = argparse.ArgumentParser(description='check read numbers into and out of sam compare, must be within minimum unique reads and sum of uniq reads from both summary files')
parser.add_argument('-b1','--bwa1',dest='bwa1', action='store', required=True, help='The bwa split sam summary file containing uniq read counts sam1 [Required]')
parser.add_argument('-b2','--bwa2',dest='bwa2', action='store', required=True, help='The bwa split sam summary file containing uniq read counts sam2 [Required]')
parser.add_argument('-fq','--fq',dest='fq', action='store', required=True, help='fastq filename [Required]')
parser.add_argument('-a','--ase',dest='ase',action='store',required=True, help='The ase totals file containing read counts generated from sam compare script [Required]')
parser.add_argument('-o','--out', dest='out', action='store', required=True, help='Output file containing check info [Required]')
args = parser.parse_args()
  

       

B1 = []
B2 = []
### Open bwa
with open(args.bwa1,'r') as bwa_table:
    B1 = csv.reader(bwa_table, delimiter= '\t')
    next(B1)
    for row in B1:
        opposite1=int(row[2])
        mapped1=int(row[4])
        uniq_b1 = opposite1 + mapped1
        #sum opposite [2] and mapped [4] = total uniq reads

with open(args.bwa2, 'r') as bwa2_table:
    B2 = csv.reader(bwa2_table, delimiter= '\t')
    next(B2)
    for row in B2:
        opposite2=int(row[2])
        mapped2=int(row[4])
        uniq_b2 = opposite2 + mapped2
        #sum opposite [2] and mapped [4] = total uniq reads

## read # in sam file should be between greater of uniq_b1 or uniq_b2 - this should be the same # as in the ase_totals table
sumReads=uniq_b1 + uniq_b2
minReads=min(uniq_b1, uniq_b2)

print(sumReads)
print(minReads)

with open(args.ase, 'r') as ase_table:
    df = pd.read_csv(ase_table, sep='\t')

    count_tot=df['Count totals:'].iloc[len(df)-1]
    print(count_tot)

if int(minReads) <= int(count_tot) <= int(2*sumReads):
    flag_readnum_in_range = 1
else:
    flag_readnum_in_range = 0


bname = os.path.basename(args.fq)
name  = os.path.splitext(bname)[0]

## counts in ase file should be betweeen minReads and the sum of uniq mapped reads 
## open file to write to
with open(args.out, 'w') as outfile:
    spamwriter=csv.writer(outfile, delimiter='\t')
    first_row = True
    
    if first_row: 
        spamwriter.writerow(['fqName', 'min_uniq_g1_uniq_g2', 'sum_uniq_g1_uniq_g2', 'total_counts_ase_table', 'flag_readnum_in_range'])
        first_row = False

        row_items = [name, minReads, sumReads, count_tot,flag_readnum_in_range]
    spamwriter.writerow(row_items)

