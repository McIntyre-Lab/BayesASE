#!/usr/bin/env python

import argparse
import os
import pandas as pd
import logging
import logging.config


def getOptions():
    parser = argparse.ArgumentParser(
        description="""Check design file for G1, G2, sampleID, fqName, fqExtension,
                       techRep, readLength columns"""
    )
    parser.add_argument(
        "-s",
        "--design",
        dest="design",
        action="store",
        required=True,
        help="Design file containing fq file names and sample ids [Required]",
    )
    parser.add_argument(
        "-d",
        "--dups",
        dest="dups",
        required=False,
        help="File containing list of duplicate fqNames in design file",
    )
    parser.add_argument(
        "-l",
        "--logfile",
        dest="logfile",
        required=True,
        help="Name of log file that checks design file",
    )
    args = parser.parse_args()
    return args


def fastq_check(logfile, design, dups):
    fqName = 'fqName'
    with open(logfile, "w") as outfile:
        df = pd.read_csv(design, sep="\t", index_col=None)
        if len(df[fqName].unique().tolist()) < len(df[fqName].tolist()):
            dups = df[df.duplicated(fqName, keep=False) == 'True']
            if dups is not None:
                outfile.write(
                    "Duplicate check:\tThere are duplicate fqName entries in your design file!"
                )
                outfile.write(f"\n\t{'-'*33}")
                outfile.write("\nDuplicated Rows:\n")
                dups.to_csv(outfile, index=False, sep="\t")
        else:
            outfile.write(
                "Duplicate check:\tNo duplicate fqName entries in your design file\t\n"
            )


def columns_check(logfile, design):
    design_identifier = os.path.splitext(os.path.basename(design))[0]
    columns = ["G1", "G2", "sampleID", "fqName", "fqExtension", "techRep", "readLength"]
    with open(logfile, "w") as outfile:
        df = pd.read_csv(design, sep="\t", index_col=None)
        headers = list(df)
        if headers != columns:
            outfile.write(
                f"""Headers check:\tERROR: column headers in file {design_identifier}
 do not align with order requirements, please check.\n{'-'*33}
Details:\n"""
            )
            for col in columns:
                if col not in df:
                    outfile.write(
                        f"\tError: column header {col} does not exist in design file."
                    )
            return -1
        if headers == columns:
            outfile.write(
                f"Header check:\tColumns in {design_identifier} align with requirements."
            )


def main():
    args = getOptions()
    logging.basicConfig(
        filename=args.logfile,
        filemode="a",
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.DEBUG,
    )
    columns_check(args.logfile, args.design)
    fastq_check(args.logfile, args.design, args.dups)


if __name__ == "__main__":
    main()
