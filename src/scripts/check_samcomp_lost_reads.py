#!/usr/bin/env python
""""
check read numbers into and out of sam compare outputs a file
"""

import argparse
import csv
import os
import pandas as pd

# Configuration
csv.field_size_limit(1000000000)


def get_args():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="check read numbers into and out of sam compare, must be within minimum unique reads and sum of uniq reads from both summary files"
    )
    parser.add_argument(
        "-b1",
        "--bwa1",
        dest="bwa1",
        action="store",
        required=True,
        help="The bwa split sam summary file containing uniq read counts sam1 [Required]",
    )
    parser.add_argument(
        "-b2",
        "--bwa2",
        dest="bwa2",
        action="store",
        required=True,
        help="The bwa split sam summary file containing uniq read counts sam2 [Required]",
    )
    parser.add_argument(
        "-fq",
        "--fq",
        dest="fq",
        action="store",
        required=True,
        help="fastq filename [Required]",
    )
    parser.add_argument(
        "-a",
        "--ase",
        dest="ase",
        action="store",
        required=True,
        help="The ase totals file containing read counts generated from sam compare script [Required]",
    )
    parser.add_argument(
        "-o",
        "--out",
        dest="out",
        action="store",
        required=True,
        help="Output file containing check info [Required]",
    )
    args = parser.parse_args()
    return args


def main():
    """
    Main entry point of the script
    Test:
    check_samcomp_lost_reads.py \
    --bwa1=galaxy/test-data/align_and_counts_test_data/W1118_G1_BWASplitSAM_summary.tabular \
    --bwa2=galaxy/test-data/align_and_counts_test_data/W55_G2_BWASplitSAM_summary.tabular \
    --fq=galaxy/test-data/align_and_counts_test_data/W55_M_1_1.fastq \
    --ase=galaxy/test-data/align_and_counts_test_data/ASE_totals_table_BASE_test_data.tsv \
    --out=check_SAM_compare_for_lost_reads_BASE_test_data.tabular
    Sample out:
    galaxy/test-data/align_and_counts_test_data/check_SAM_compare_for_lost_reads_BASE_test_data.tabular
    """
    args = get_args()
    with open(args.bwa1, "r") as bwa_table:
        B1 = csv.reader(bwa_table, delimiter="\t")
        # Discard the header
        next(B1)
        row = next(B1)
        opposite1 = int(row[2])
        mapped1 = int(row[4])
        # Total unique reads = sum of the opposite [2] and mapped [4] columns
        uniq_b1 = opposite1 + mapped1

    with open(args.bwa2, "r") as bwa2_table:
        B2 = csv.reader(bwa2_table, delimiter="\t")
        # Discard the header
        next(B2)
        row = next(B2)
        opposite2 = int(row[2])
        mapped2 = int(row[4])
        # Total unique reads = sum of the opposite [2] and mapped [4] columns
        uniq_b2 = opposite2 + mapped2

    # Read number in the sam file should be between greater of uniq_b1 or uniq_b2.
    # It should be the same number as in the ase_totals table.
    sumReads = uniq_b1 + uniq_b2
    minReads = min(uniq_b1, uniq_b2)

    with open(args.ase, "r") as ase_table:
        df = pd.read_csv(ase_table, sep="\t")
        count_tot = int(df["Count totals:"].iloc[len(df) - 1])

    if minReads <= count_tot <= sumReads * 2:
        flag_readnum_in_range = 1
    else:
        flag_readnum_in_range = 0

    bname = os.path.basename(args.fq)
    name = os.path.splitext(bname)[0]

    ## counts in ase file should be betweeen minReads and the sum of uniq mapped reads
    ## open file to write to
    with open(args.out, "w") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(
            [
                "fqName",
                "min_uniq_g1_uniq_g2",
                "sum_uniq_g1_uniq_g2",
                "total_counts_ase_table",
                "flag_readnum_in_range",
            ]
        )
        row_items = [name, minReads, sumReads, count_tot, flag_readnum_in_range]
        writer.writerow(row_items)


if __name__ == "__main__":
    main()
