#!/usr/bin/env python
"""
Check that user's Pre-Bayesian design file adheres to BASE requirements
Make sure that the headers are in the correct order and file is properly formatted
"""

import argparse
import os
import pandas as pd


def get_args():
    """Process command-line arguments"""
    parser = argparse.ArgumentParser(description="""Check user-supplied Pre-Bayesian design file for
                                     correct formatting and adherence to BASE guidelines""")
    parser.add_argument('-design','--design',dest='design', action='store', required=True,
                        help='Input Design File. See BASE User Guide for formatting help [REQUIRED]')
    parser.add_argument('-compNum','--compNum',dest='compNum',type=int, action='store', required=True,
                        help='Number of comparates')
    parser.add_argument('-o','--out', dest='out', action='store', required=True,
                        help='Name of log file that checks design file')
    args = parser.parse_args()
    return args


def err_msg(col):
    """Create an error message"""
    return f"\tError: column '{col}' does not exist or is mislabeled in design file\n"


def main():
    """
    Check that the correct columns exist in design file and are in the correct order.
    """
    args = get_args()
    df=pd.read_csv(args.design, sep='\t', index_col=None)
    headers=df.columns.tolist()

    in_file = os.path.split(args.design)[1]
    general_success_msg = f'\tThe columns are labeled correctly and are in the correct order\n'
    general_error_msg = f"""\tError: Design file format does not align with BASE requirements.
{' '*6}\tColumn names are either incorrectly labeled, missing, or out of order\n"""

    column_names = {'g1': 'C1_G1', 'g2': 'C1_G2', 'c1': 'C2_G1', 'c2': 'C2_G2',
                    'comparate_1': 'Comparate_1', 'comparate_2': 'Comparate_2', 'compID': 'compID'}
    fixed_column_ids = {1: ['g1', 'g2', 'comparate_1', 'compID'],
                        2: ['g1', 'g2', 'c1', 'c2', 'comparate_1', 'comparate_2', 'compID']}
    column_id_list = fixed_column_ids[args.compNum]
    fixed_column_names = [column_names[x] for x in column_id_list]

    with open(args.out, 'w') as outfile:
        outfile.write(f'Design_file_name: {in_file}\n')
        if headers != fixed_column_names:
            outfile.write(general_error_msg)
            for column_name in fixed_column_names:
                if column_name not in headers:
                    msg = err_msg(column_name)
                    outfile.write(msg)
        else:
            outfile.write(general_success_msg)


if __name__ == '__main__':
    main()
