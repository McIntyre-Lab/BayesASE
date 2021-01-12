#!/usr/bin/env python3

import argparse
import os
import subprocess
import pandas as pd
try:
    from importlib import resources as ires
except ImportError:
    import importlib_resources as ires

DEBUG = False


def getOptions():
    parser = argparse.ArgumentParser(description="Run bayesian model")
    parser.add_argument(
        "-d",
        "--design",
        action="store",
        help="TSV design file with sampleID names to analyze",
    )
    parser.add_argument(
        "-i",
        "--infile",
        action="store",
        help="TSV input file with merged comparates and new headers",
    )
    parser.add_argument(
        "-c",
        "--cond",
        action="store",
        required=False,
        help="Number of conditions",
    )
    parser.add_argument(
        "-t",
        "--iterations",
        action="store",
        type=int,
        default=100000,
        help="Optional number of iterations (default: 100000)",
    )
    parser.add_argument(
        "-w",
        "--warmup",
        action="store",
        type=int,
        default=10000,
        help="Optional number of warmups (default: 10000)",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        required=False,
        help="Output file name/path. Default - bayesian_output_$name.tabular",
    )
    parser.add_argument(
        "-r",
        "--rscript",
        action="store",
        required=False,
        help="Full path to R script if not using package version",
    )
    parser.add_argument(
        "-s",
        "--stanmodel",
        action="store",
        required=False,
        help="Full path to stan model if not using package version",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    return args


def main():
    args = getOptions()
    global DEBUG
    if args.debug:
        DEBUG = True
    input_file = args.infile
    if DEBUG:
        print(f"DEBUG: input_file: {input_file}")

    # (1) Parsing datafile to extract rows with sampleID specified in design file, set c1 and c2
    # Standardized Paths##

    # Read in design file as dataframe
    df = pd.read_csv(args.design, sep="\t")

    # iterate over design file
    for index, row in df.iterrows():

        # Make variable for number of conditions
        compnum = args.cond

        df.set_index("Comparate_1")

        comparison = row["compID"]
        c1 = row["Comparate_1"]
        c2 = row["Comparate_2"]

        del row["compID"]
        row = row.to_frame()

        infile = pd.read_csv(input_file, index_col=None, header=0, sep="\t")

        infile.set_index("FEATURE_ID")

        # add comparison column (last)
        infile["comparison"] = comparison

        datafile2 = os.path.abspath(comparison + "_temp")

        infile.to_csv(datafile2, na_rep="NA", index=False)

        rout = comparison + "_r_out"
        routput = os.path.join(os.curdir, rout)

        # Compiled stan model
        if not args.rscript:
            with ires.path("BayesASE.data", "nbmodel_stan2_flex_prior.R") as R_path:
                r_script = str(R_path)
        else:
            r_script = args.rscript
        if not args.stanmodel:
            with ires.path("BayesASE.data", "environmentalmodel2.stan") as stan_path:
                stan_file = str(stan_path)
        else:
            stan_file = args.stanmodel

        # (2) Run R script where args1 is the input csv and args2 is the output path for NBmodel.R
        cmd = [
                "Rscript",
                r_script,
                stan_file,
                datafile2,
                routput,
                str(compnum),
                os.curdir,
                str(args.iterations),
                str(args.warmup),
            ]

        print(" ".join(cmd))

        subprocess.call(cmd)

        # (3) Format input from Rscript and get list of default header names
        # Change headers back to actual comparates from c1 and c2
        df2 = pd.read_csv(routput)

        headers_out = list(df2.columns.values)

        for a in range(len(headers_out)):
            if "c1" in headers_out[a]:
                headers_out[a] = headers_out[a].replace("c1", c1)
            if "c2" in headers_out[a]:
                headers_out[a] = headers_out[a].replace("c2", c2)

        df2.columns = headers_out

        if not args.outfile:
            outfile = "bayesian_out_" + comparison + ".tabular"
        else:
            outfile = args.outfile

        df2.to_csv(outfile, na_rep="NA", index=False, sep="\t")


if __name__ == "__main__":
    main()
