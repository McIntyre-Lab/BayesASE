#!/usr/bin/env python3

import argparse
from functools import reduce
import pandas as pd

# Merge filtered/summarized files with qsim values by user-specified comparison

DEBUG = False


def getOptions():
    parser = argparse.ArgumentParser(
        description="Merges filtered/summarized comparate count tables as specified by user."
    )
    parser.add_argument(
        "-output",
        "--output",
        dest="output",
        action="store",
        required=True,
        help="Output directory for complete merged comparate files ready for Bayesian",
    )
    parser.add_argument(
        "-collection_identifiers",
        "--collection_identifiers",
        dest="collection_identifiers",
        action="store",
        required=True,
        help="ASE count table collection identifiers",
    )
    parser.add_argument(
        "-collection_filenames",
        "--collection_filenames",
        dest="collection_filenames",
        action="store",
        required=True,
        help="ASE count table collection filenames",
    )
    parser.add_argument(
        "-design",
        "--design",
        dest="design",
        action="store",
        required=True,
        help="Design file",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Print debugging output"
    )
    args = parser.parse_args()
    return args


def main():
    args = getOptions()
    global DEBUG
    if args.debug:
        DEBUG = True

    identifiers = [i.strip() for i in args.collection_identifiers.split(",")]
    filenames = [i.strip() for i in args.collection_filenames.split(",")]
    input_dict_comp = dict(zip(identifiers, filenames))
    if DEBUG:
        print(f"DEBUG: input dict:\n{input_dict_comp}")

    df_design = pd.read_csv(args.design, sep="\t")
    if DEBUG:
        print(f"DEBUG: design:\n{df_design}")

    # Create subset of design file of comparate specification columns (will quantify # comparates
    # by number of columns left) Store compID to name output file
    c1_list = df_design["Comparate_1"].tolist()
    c2_list = df_design["Comparate_2"].tolist()

    # Change name of dictionary since it conflicts with dictionary name used for collections
    sample_dict = {}
    row_list = []
    comparison_list = df_design["compID"].tolist()
    del df_design["compID"]

    # Create dictionaries per design file row to store the row's comparate files
    for index, sample in df_design.iterrows():
        sample_dict[index] = list(sample)
    if DEBUG:
        print(f"DEBUG: sample_dict:\n{sample_dict}")
    # If there are comparison columns (column # > 1)
    for key in sample_dict:
        row_list = sample_dict[key]
        file_list = []
        comp_dict = {}
        comparison = comparison_list[key]
        c1 = c1_list[key]
        c2 = c2_list[key]
        for i, comp in enumerate(row_list):
            if DEBUG:
                print(f"DEBUG: comparison:\n{comp}")
            comp_dict[i + 1] = comp

            # Assign filename so it can be called
            # Keep file names that Galaxy assigns so that Galaxy can recognize the collection
            row_list[i] = input_dict_comp[comp]

            # Change pd.read_csv to pd.read_table to read file into dataframe
            file = pd.read_table(row_list[i], index_col=None, header=0)
            file_list.append(file)

        df_merged = reduce(lambda x, y: pd.merge(x, y, on=["FEATURE_ID"]), file_list)

        # Drop columns you don't want before merge
        df_merged = df_merged[
            df_merged.columns.drop(list(df_merged.filter(regex="comp")))
        ]

        df_merged.set_index("FEATURE_ID", inplace=True)

        merged_headers = list(df_merged.columns.to_numpy())
        # For stan model, requires headers to have general comparate input names
        # This reassigns comparate names to be c1, c2, c3... depending on design file specs
        for x in comp_dict:
            for i in range(len(merged_headers)):
                if c1 in merged_headers[i]:
                    merged_headers[i] = merged_headers[i].replace(c1, "c1")
                if c2 in merged_headers[i]:
                    merged_headers[i] = merged_headers[i].replace(c2, "c2")

        df_merged.columns = merged_headers
        df_filtered = df_merged

        # Output tsv file, without an extension so that next script knows what name to expect
        outfile = args.output + "/bayesian_input_" + comparison
        df_filtered.to_csv(outfile, sep="\t")


if __name__ == "__main__":
    main()
