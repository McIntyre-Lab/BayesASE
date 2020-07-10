#!/usr/bin/env python3
import csv, sys, argparse, os, itertools, operator, collections, logging
import logging.config
import pandas as pd
import numpy as np

# McLab Packages
#import mclib_Python as mclib

parser = argparse.ArgumentParser(description='Check number of reads per FQ file into and out of sam compare')
parser.add_argument('-fq','--fq',dest='fq', action='store', required=True, help='Name of the fq file]')
parser.add_argument('-alnType','--alnType',dest='alnType', action='store', required=False, default="SE", choices=("SE", "PE"), help='Input SE for single end or PE for paired end alignments [Default = SE]')
parser.add_argument('-s1', '--sam1', dest='sam1', action='store', required=True, help='sam file used in sam compare script, aligned to G1 [Required]')
parser.add_argument('-s2', '--sam2', dest='sam2', action='store', required=True, help='sam file used in sam compare script, aligned to G2 [Required]')
#parser.add_argument('-samPath','--samPath',dest='samPath', action='store', required=True, help='Path to sam files [Required]')
parser.add_argument('-G1','--G1',dest='G1', action='store', required=True, help='Name of G1 [Required]')
parser.add_argument('-G2','--G2',dest='G2', action='store', required=True, help='Name of G2 [Required]')

# output file
parser.add_argument('-o','--out', dest='out', action='store', required=True, help='Output file containing info on whether each fq file has 2 sam files [Required]')
args = parser.parse_args()
 
### For every FQ file run, should have 2 sam files
### Append sam files to an array

fq_file = os.path.split(args.fq)[1]

sam1 = args.sam1
sam2 = args.sam2
print(sam1)
#samPath= args.samPath
#sam1=args.samPath + '/' + args.G2 + '_' + args.fq + '_upd_feature_uniq.sam'
#sam2=args.samPath + '/' + args.G1 + '_' + args.fq + '_upd_feature_uniq.sam'

sarray=[]
sarray.append(sam1)
sarray.append(sam2)

#print(sarray)
### FQ files, num is 1 for SE, represents fq per 2 sam files

### Before Sam compare
with open(args.out, 'w') as outfile:
    first_row = True

    if first_row:
        outfile.write('fqName' + ',' + 'message\n')
        first_row = False

    if args.alnType=='SE':
        num=1
        if len(sarray) != 2*num:
            outfile.write(fq_file + ',' + 'Do NOT have 2 SAM files - rerun alignments to updated genomes!/n')
        else:
            #Continue with sam compare
            outfile.write(fq_file + ',' + 'Have 2 SAM files - good!\n')
    elif args.alnType=='PE':
        num=2
        if len(sarray)*2 != 2*num:
            outfile.write(fq_file + ',' + 'Do NOT have 2 SAM files - rerun alignments to updated genomes!\n')
        else:
            #Continue with sam compare
            outfile.write('Have 2 SAM files - good!\n')
    else:
        outfile.write(fq_file + ',' + 'Select whether you ran SE or PE alignments!\n')
