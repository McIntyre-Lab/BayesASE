#!/usr/bin/env python
"""
In alignment summary file, total_reads = sum(count_mapped_read_oposite_strand + count_unmapped_read
+ count_mapped_read + count_ambiguous_read)
"""

import csv, sys, argparse, os, itertools, operator, collections
import pandas as pd
import numpy as np


def get_args():
    parser = argparse.ArgumentParser(description="""check total reads column in alignment file match
                                                 the sum of the other columns""")
    parser.add_argument('-a1','--alnSum1',dest='alnSum1', action='store', required=True,
                        help='The G1 alignment summary file containing all read types [Required]')
    parser.add_argument('-a2','--alnSum2',dest='alnSum2', action='store', required=True,
                        help='The G2 alignment summary file containing all read types [Required]')
    parser.add_argument('-fq','--fq', dest='fq', action='store', required=True,
                        help='FQ file used in alignment [Required]')
    parser.add_argument('-o','--out', dest='out', action='store', required=True,
                        help='Output file containing check info [Required]')
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    with open(args.fq, 'r') as fq:
        reads = []
        for line in fq:
            if line.startswith("@"):
                reads.append(line)
    start_reads = len(reads)
    bname = os.path.basename(args.fq)
    name  = os.path.splitext(bname)[0]

    with open(args.alnSum1, 'r') as sum_table1:
        sumT1=csv.reader(sum_table1, delimiter='\t')
        next(sumT1)
        for row in sumT1:
            opp1=int(row[2])
            unmap1=int(row[3])
            mapread1=int(row[4])
            amb1=int(row[5])
            end_reads1 = opp1 + unmap1 + mapread1 + amb1

    with open(args.alnSum2, 'r') as sum_table2:
        sumT2=csv.reader(sum_table2, delimiter='\t')
        next(sumT2)
        for row in sumT2:
            opp2=int(row[2])
            unmap2=int(row[3])
            mapread2=int(row[4])
            amb2=int(row[5])
            end_reads2 = opp2 + unmap2 + mapread2 + amb2

    if start_reads == end_reads1:
        flag_start_readNum_eq_end_readNum_G1 = 1
    else:
        flag_start_readNum_eq_end_readNum_G1 = 0

    if start_reads == end_reads2:
        flag_start_readNum_eq_end_readNum_G2 = 1
    else:
        flag_start_readNum_eq_end_readNum_G2 = 0

    with open(args.out, 'w') as outfile:
        csvwriter=csv.writer(outfile, delimiter='\t')
        header = ['fqName', 'start_read_num', 'readNum_G1', 'readNum_G2',
                  'flag_start_readNum_eq_readNum_G1', 'flag_start_readNum_eq_readNum_G2']
        csvwriter.writerow(header)
        row_items = [name, start_reads, end_reads1, end_reads2,
                     flag_start_readNum_eq_end_readNum_G1,
                     flag_start_readNum_eq_end_readNum_G2]
        csvwriter.writerow(row_items)


if __name__ == '__main__':
    main()

