#!/usr/bin/env python3
"""Verify that the sam files selected as tool arguments exist on the filesystem."""

import argparse
import os
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser(
        description="Check number of reads per FQ file into and out of sam compare"
    )
    parser.add_argument(
        "-fq",
        "--fq",
        dest="fq",
        action="store",
        required=True,
        help="Name of the fq file]",
    )
    parser.add_argument(
        "-alnType",
        "--alnType",
        dest="alnType",
        action="store",
        required=False,
        default="SE",
        choices=("SE", "PE"),
        help="Input SE for single end or PE for paired end alignments [Default = SE]",
    )
    parser.add_argument(
        "-s1",
        "--sam1",
        dest="sam1",
        action="store",
        required=True,
        help="sam file used in sam compare script, aligned to G1 [Required]",
    )
    parser.add_argument(
        "-s2",
        "--sam2",
        dest="sam2",
        action="store",
        required=True,
        help="sam file used in sam compare script, aligned to G2 [Required]",
    )
    parser.add_argument(
        "-o",
        "--out",
        dest="outfile",
        action="store",
        required=True,
        help="Output file containing info on whether each fq file has 2 sam files [Required]",
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    fq_p = Path(args.fq)
    fq_file = fq_p.name
    out_path = Path(args.outfile)
    out_dir = out_path.parent
    # Galaxy creates a working directory for output, so don't mind that out_dir exists
    out_dir.mkdir(exist_ok=True)
    error = False
    with open(out_path, "w") as out_fh:
        out_fh.write(f"{fq_file}\tmessage\n")
        if args.sam1 and args.sam2:
            p_sam1 = Path(args.sam1)
            p_sam2 = Path(args.sam2)
            if not p_sam1.exists():
                out_fh.write(
                    f"{fq_file}\tError: missing {args.sam1} SAM file. Realign to updated genomes!\n"
                )
                error = True
            if not p_sam2.exists():
                out_fh.write(
                    f"{fq_file}\tError: missing {args.sam2} SAM file. Realign to updated genomes!\n"
                )
                error = True
        if not error:
            out_fh.write(f"{fq_file}\tSuccess: located both SAM files as expected.")


if __name__ == "__main__":
    main()
