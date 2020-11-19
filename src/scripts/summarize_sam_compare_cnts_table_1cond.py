#!/usr/bin/env python3
"""
Prep sam compare data for Bayesian Machine
Logic:
*  group df by sample,
*  only keep samples with more than 2 reps
*  summarize columns
*  filtering
*  calculate:
*  total_reads_counted
*  both total
*  g1_total
*  g2 total
*  ase total
*  for each rep, if APN > input then
*    flag_APN = 1 (flag_APN = 0 if APN < input, flag_APN = -1 if APN < 0)
*  if flag_APN = 1 for at least 1 of the reps the
*    flag_analyze = 1
*   merge reps together
"""

import argparse
import os
import pandas as pd
import numpy as np
from functools import reduce

DEBUG = False


def getOptions():
    parser = argparse.ArgumentParser(description="Return best row in blast scores file")
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        action="store",
        required=True,
        help="Output directory for filtered ase counts",
    )
    parser.add_argument(
        "-collection_identifiers",
        "--collection_identifiers",
        dest="collection_identifiers",
        action="store",
        required=True,
        help="Input original names [Required]",
    )
    parser.add_argument(
        "-collection_filenames",
        "--collection_filenames",
        dest="collection_filenames",
        action="store",
        required=True,
        help="Input galaxy names [Required]",
    )
    parser.add_argument(
        "-d",
        "--design",
        dest="design",
        action="store",
        required=True,
        help="Design file",
    )
    parser.add_argument(
        "-p1",
        "--parent1",
        dest="parent1",
        action="store",
        required=True,
        help="Column containing parent 1 genome, G1",
    )
    parser.add_argument(
        "-p2",
        "--parent2",
        dest="parent2",
        action="store",
        required=True,
        help="Column containing parent 2 genome, G2",
    )
    parser.add_argument(
        "-s",
        "--sampleCol",
        dest="sampleCol",
        action="store",
        required=True,
        help="Column containing sample names, no rep info",
    )
    parser.add_argument(
        "-id",
        "--sampleIDCol",
        dest="sampleIDCol",
        action="store",
        required=True,
        help="Column containing sampleID names, has rep info",
    )
    parser.add_argument(
        "-a",
        "--apn",
        dest="apn",
        action="store",
        required=True,
        type=int,
        help="APN (average per nucleotide) value for flagging a feature as found and analyzable",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Print debugging output"
    )

    args = parser.parse_args()
    return args


def main():
    """Main Function"""
    args = getOptions()
    global DEBUG
    if args.debug:
        DEBUG = True

    identifiers = [i.strip() for i in args.collection_identifiers.split(",")]
    filenames = [i.strip() for i in args.collection_filenames.split(",")]
    input_dict = dict(zip(identifiers, filenames))

    # Read in design file as dataframe (as a TSV file)
    df_design = pd.read_table(args.design, header=0)

    # Set columns to use for counting reps per sample
    parent1 = args.parent1
    parent2 = args.parent2
    sampleCol = args.sampleCol
    sampleIDCol = args.sampleIDCol

    df_design["numReps"] = df_design.groupby([parent2, sampleCol])[sampleCol].transform("count")
    if DEBUG:
        print("DEBUG: design df:\n{}".format(df_design))

    # Cumulative counter variables for each comparate
    df_design["seqCnt"] = df_design.groupby([parent2, sampleCol]).cumcount() + 1

    df_dict = {}
    df_grouped = df_design.loc[df_design.seqCnt > 0]
    if DEBUG:
        print("DEBUG: design grouped:\n{}".format(df_grouped))

    for index, comparate in df_grouped.iterrows():
        if DEBUG:
            print("DEBUG: comparate:\n{}".format(comparate))
        # count_good is the number for each line comparison
        g1 = comparate[parent1]
        g2 = comparate[parent2]
        count_good = comparate["seqCnt"]
        sample_id = comparate[sampleIDCol]
        sample_id2 = sample_id.rsplit("_", 1)[0]
        numReps = comparate["numReps"]
        repCnt = sample_id2 + "_num_reps"
        g1_total = (
            "counts_" + sample_id2 + "_" + "g1_total" + "_" + "rep" + str(count_good)
        )
        g2_total = (
            "counts_" + sample_id2 + "_" + "g2_total" + "_" + "rep" + str(count_good)
        )
        both_total = (
            "counts_" + sample_id2 + "_" + "both_total" + "_" + "rep" + str(count_good)
        )
        flag_apn = sample_id2 + "_" + "flag_apn" + "_" + "rep" + str(count_good)
        APN_total_reads = (
            sample_id2 + "_" + "APN_total_reads" + "_" + "rep" + str(count_good)
        )
        APN_both = sample_id2 + "_" + "APN_both" + "_" + "rep" + str(count_good)

        inFile = sample_id
        samC = input_dict[inFile]
        if DEBUG:
            print("DEBUG: samC file:\n{}".format(samC))
        try:
            samFile = pd.read_table(samC, header=0)
        except OSError:
            print("ERROR: Missing file:\n{}".format(samC))
            continue
        samFile[both_total] = samFile["BOTH_EXACT"] + samFile["BOTH_INEXACT_EQUAL"]

        samFile[g2_total] = (
            samFile["SAM_A_ONLY_EXACT"]
            + samFile["SAM_A_ONLY_SINGLE_INEXACT"]
            + samFile["SAM_A_EXACT_SAM_B_INEXACT"]
            + samFile["SAM_A_INEXACT_BETTER"]
        )

        samFile[g1_total] = (
            samFile["SAM_B_ONLY_EXACT"]
            + samFile["SAM_B_ONLY_SINGLE_INEXACT"]
            + samFile["SAM_B_EXACT_SAM_A_INEXACT"]
            + samFile["SAM_B_INEXACT_BETTER"]
        )

        samFile[APN_total_reads] = samFile["APN_total_reads"]
        samFile[APN_both] = samFile["APN_both"]

        # if APN > user-specified value then flag_APN = 1
        samFile.loc[:, flag_apn] = 0
        samFile.loc[samFile.APN_total_reads > args.apn, flag_apn] = 1
        samFile.loc[samFile.APN_total_reads == 0, flag_apn] = 0
        samFile.loc[samFile.APN_total_reads < 0, flag_apn] = -1
        samFile[flag_apn] = pd.to_numeric(samFile[flag_apn], errors="ignore")

        sam_subset = samFile[
            [
                "FEATURE_ID",
                g1_total,
                g2_total,
                both_total,
                flag_apn,
                APN_total_reads,
                APN_both,
            ]
        ]

        sam_subset = sam_subset.assign(g1=g1)
        sam_subset = sam_subset.assign(g2=g2)
        sam_subset[repCnt] = numReps

        df_dict[sample_id] = sam_subset

        comp_list = [
            value for key, value in df_dict.items() if key.startswith(sample_id2)
        ]

        # Need these column headers to merge on
        comp_reps = sample_id2 + "_num_reps"

        # Merge c1 and c2 dataframes separately
        comp_merged = reduce(
            lambda x, y: pd.merge(
                x, y, on=["FEATURE_ID", "g1", "g2", comp_reps], how="outer"
            ),
            comp_list,
        )

        # Create flag_analyze for each comparate, pull out all flag_apn using pattern match
        # sum flag_apn for each comparate, if flag_sum  > 0
        # set new column comparison_flag_analyze  = 1

        comp_flag_analyze = sample_id2 + "_flag_analyze"

        flag_comp_cols = [col for col in comp_merged.columns if "flag_apn" in col]
        comp_merged.loc[:, "flag_sum"] = comp_merged[flag_comp_cols].sum(axis=1)
        comp_merged.loc[:, comp_flag_analyze] = np.where(
            comp_merged["flag_sum"] > 0, 1, 0
        )
        del comp_merged["flag_sum"]

        # Order column headers for output
        comp_reps_headers = []
        for each in list(comp_merged.columns.values):
            if sample_id2 in each and "rep" in each and "num" not in each:
                comp_reps_headers.append(each)
        ordered_headers = [
            "FEATURE_ID",
            "g1",
            "g2",
            sample_id2 + "_flag_analyze",
            sample_id2 + "_num_reps",
        ] + comp_reps_headers

        # Change so output file will properly recognized by the next script in the workflow
        # outfilename = "ase_counts_filtered_" + sample_id2 + ".csv"
        outfilename = "ase_counts_filtered_" + sample_id2
        outfile = os.path.join(args.output, outfilename)

        comp_merged = comp_merged[ordered_headers]
        comp_merged.to_csv(outfile, index=False, sep="\t")


if __name__ == "__main__":
    main()
