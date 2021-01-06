#!/usr/bin/env python3

import argparse
import os
import pandas as pd
import sys

# Configuration
default_data_columns = [
    "FEATURE_ID",
    "BOTH_EXACT",
    "BOTH_INEXACT_EQUAL",
    "SAM_A_ONLY_EXACT",
    "SAM_B_ONLY_EXACT",
    "SAM_A_EXACT_SAM_B_INEXACT",
    "SAM_B_EXACT_SAM_A_INEXACT",
    "SAM_A_ONLY_SINGLE_INEXACT",
    "SAM_B_ONLY_SINGLE_INEXACT",
    "SAM_A_INEXACT_BETTER",
    "SAM_B_INEXACT_BETTER",
]


def getOptions():
    parser = argparse.ArgumentParser(
        description="Sum ase counts across tech reps (by sampleID) using the provided design file"
    )
    parser.add_argument(
        "--design",
        type=str,
        action="store",
        required=True,
        help="Alignment Design File containing fastq fqNames and sampleIDs [Required]",
    )
    parser.add_argument(
        "--sim",
        action="store_true",
        help="Select if this is a simulation dataset",
    )
    parser.add_argument(
        "--bed",
        action="store",
        required=True,
        help="Full path to the bed file [Required]",
    )
    parser.add_argument(
        "--collection_identifiers",
        action="store",
        required=True,
        help="Input original names [Required]",
    )
    parser.add_argument(
        "--collection_filenames",
        action="store",
        required=True,
        help="Input galaxy names [Required]",
    )
    parser.add_argument(
        "--begin",
        type=int,
        action="store",
        help="Start point in design file [Optional]",
    )
    parser.add_argument(
        "--end",
        type=int,
        action="store",
        help="End point in design file [Optional]",
    )
    parser.add_argument(
        "--outdesign",
        action="store",
        required=True,
        help="Output design file name with full path in galaxy [Required]",
    )
    parser.add_argument(
        "--outdir",
        action="store",
        required=True,
        help="Output directory for summed count table files [Required]",
    )
    if len(sys.argv) < 2:
        parser.print_help()
        parser.exit()
    args = parser.parse_args()
    return args


def headers_check(single_file, file_identifier):
    """Check column names in a count tables file"""
    df = pd.read_table(single_file)
    columns = list(df)
    if columns != default_data_columns:
        return f"ERROR: Incorrect column names in '{file_identifier}'"
    else:
        return None


def sum_counts(input_dict, df_design, out_dir, feature_lengths=False):
    df_grouped = df_design.groupby("sampleID").agg(lambda x: x.tolist())
    grouped_fastqs = df_grouped["fqName"]
    errors = []
    for sampleID, filelist in grouped_fastqs.iteritems():
        ddict = {}
        dfsum = pd.DataFrame(index=range(0), columns=default_data_columns)
        dfsum.set_index("FEATURE_ID", inplace=True)
        for ind, fqName in enumerate(filelist):
            if fqName not in input_dict:
                errors.append(f"Error: Cannot find {fqName} file in the input collection!")
                continue
            check_result = headers_check(input_dict[fqName], fqName)
            if check_result:
                errors.append(check_result)
                continue
            # Dictionary to store each count table as a dataframe with fastq name as a key
            ddict[fqName] = pd.read_table(input_dict[fqName])
            if not feature_lengths:
                ddict[fqName].set_index("FEATURE_ID", inplace=True)
                dfsum = dfsum.add(ddict[fqName], fill_value=0)
            else:
                dfsum = count_totals(df_design, ind, ddict, dfsum, fqName, feature_lengths)
        # Drop intermediate columns we no longer need after real data total calculations
        dfout = dfsum.drop(
            ["both x RL", "total x RL", "both_total", "total_reads_counted"], axis=1,
            errors='ignore'
        )
        outfile = os.path.join(out_dir, sampleID)
        dfout.to_csv(outfile, sep="\t")
    if errors:
        raise ValueError("\n".join(errors))
        sys.exit(1)


def count_totals(df_design, ind, ddict, dfsum, fqName, feature_lengths):
    """
    For real data calculate additional totals and add the columns to the dataframe and return dfout
    to save to csv.
    """
    ddict[fqName]["total_reads_counted"] = (
        ddict[fqName]["BOTH_EXACT"]
        + ddict[fqName]["BOTH_INEXACT_EQUAL"]
        + ddict[fqName]["SAM_A_ONLY_EXACT"]
        + ddict[fqName]["SAM_A_ONLY_SINGLE_INEXACT"]
        + ddict[fqName]["SAM_A_EXACT_SAM_B_INEXACT"]
        + ddict[fqName]["SAM_A_INEXACT_BETTER"]
        + ddict[fqName]["SAM_B_ONLY_EXACT"]
        + ddict[fqName]["SAM_B_ONLY_SINGLE_INEXACT"]
        + ddict[fqName]["SAM_B_EXACT_SAM_A_INEXACT"]
        + ddict[fqName]["SAM_B_INEXACT_BETTER"]
    )
    ddict[fqName]["both_total"] = (
        ddict[fqName]["BOTH_EXACT"] + ddict[fqName]["BOTH_INEXACT_EQUAL"]
    )
    readLength = df_design.iloc[ind].loc["readLength"]  # Read length from design
    ddict[fqName]["both x RL"] = ddict[fqName]["both_total"] * readLength
    ddict[fqName]["total x RL"] = ddict[fqName]["total_reads_counted"] * int(readLength)
    ddict[fqName] = ddict[fqName].set_index("FEATURE_ID")
    dfsum = dfsum.add(ddict[fqName], fill_value=0)
    dfsum["APN_both"] = dfsum["both x RL"] / feature_lengths
    dfsum["APN_total_reads"] = dfsum["total x RL"] / feature_lengths
    return dfsum


def main():
    args = getOptions()
    identifiers = [i.strip() for i in args.collection_identifiers.split(",")]
    filenames = [i.strip() for i in args.collection_filenames.split(",")]
    input_dict = dict(zip(identifiers, filenames))
    df_design = pd.read_table(args.design)
    os.makedirs(args.outdir, mode=0o775, exist_ok=True)
    if args.begin and args.end:
        df_design = df_design[args.begin-2:args.end-1]
    if args.sim:  # Simulated counts
        # Sum counts tables and write them out to csv files
        sum_counts(input_dict, df_design, args.outdir, False)
        # Reformat input design file and output outdesign file
        df_design["sample"] = df_design["sampleID"].str.rsplit("_", 1).str[0]
        df_drop = df_design.drop(["fqName", "readLength", "fqExtension", "techRep"], axis=1)
        df_unique = df_drop.drop_duplicates()
        df_unique.to_csv(os.path.join(args.outdir, args.outdesign), index=False, sep="\t")
    else:  # Measured counts
        df_bed = pd.read_table(args.bed, names=["col", "start", "end", "FEATURE_ID"])
        df_bed.set_index(["FEATURE_ID"], inplace=True)
        lengths = df_bed.end - df_bed.start
        feature_lengths = lengths.tolist()
        # Sum counts tables and write them out to csv files
        sum_counts(input_dict, df_design, args.outdir, feature_lengths)
        # Create a new design file with g1, g2, sampleID columns. Add empty columns for comparison
        # 1 and 2. Output to the 'outdir' directory if a subset of the design is given, the new
        # design file will be created from that subset of the original design
        df_design["comparate"] = df_design["sampleID"].str.rsplit("_", 1).str[0]
        df_drop = df_design.drop(["fqName", "readLength", "fqExtension", "techRep"], axis=1)
        df_unique = df_drop.drop_duplicates()
        df_unique.to_csv(os.path.join(args.outdir, args.outdesign), index=False, sep="\t")


if __name__ == "__main__":
    main()
