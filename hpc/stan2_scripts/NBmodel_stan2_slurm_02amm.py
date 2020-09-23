#! /usr/bin/Rscript
import subprocess
import os
import pandas as pd
import argparse
import re

def getOptions():
    parser = argparse.ArgumentParser(description= "Run bayesian model")
    parser.add_argument("-datafile","--datafile",dest="datafile",action="store",required=True,help="Provide path for input datafile [CSV]")
    parser.add_argument("-c1_g1","--c1_g1",dest="c1_g1",action="store",required=True,help="Provide condition 1 for G1")
    parser.add_argument("-c1_g2","--c1_g2",dest="c1_g2",action="store",required=True,help="Provide condition 1 for G2")
    parser.add_argument("-c2_g1","--c2_g1",dest="c2_g1",action="store",required=True,help="Provide condition 2 for G1")
    parser.add_argument("-c2_g2","--c2_g2",dest="c2_g2",action="store",required=True,help="Provide condition 2 for G2")
    parser.add_argument("-compID","--compID",dest="compID",action="store",required=True,help="Provide comparison identifier")
    parser.add_argument("-comparate_1","--comparate_1",dest="comparate_1",action="store",required=True,help="Provide comparate 1")
    parser.add_argument("-comparate_2","--comparate_2",dest="comparate_2",action="store",required=True, help="Provide comparate 2")
    parser.add_argument("-datafile2","--datafile2",dest="datafile2",action="store",required=True,help="Provide temp path for created datafile with headers for Bayesian")
    parser.add_argument("-cond","--cond", dest="cond", action="store", required=False, help="Number of conditions")
    parser.add_argument("-workdir","--workdir", dest="workdir", action="store", required=True, help="Path to R code")
    parser.add_argument("-routput","--routput", dest="routput", action="store", required=False, help="Optional R output file")
    parser.add_argument("-subpath","--subpath", dest="subpath", action="store", required=True, help="Bayesian R script subprocess path")
    parser.add_argument("-iterations","--iterations", dest="iterations", action="store", required=False, help="Optional number of iterations (default 100000)")
    parser.add_argument("-warmup","--warmup", dest="warmup", action="store", required=False, help="Optional number of warmup (default 10000)")
    parser.add_argument("-o","--output",dest="output",action="store", required=True,help="Output path for merged file[CSV]")
    args=parser.parse_args()
    return(args)
    args = parser.parse_args()

def main():
    args = getOptions()
    
    ##(1) Parsing datafile to extract rows with sampleID specified in design file, set c1 and c2

    ##Standardized Paths##
    args.output = os.path.abspath(args.output)
    args.routput = os.path.abspath(args.routput)

    ## Read in design file as dataframe
    #df = pd.read_csv(args.design, sep=',')

    ## iterate over design file
    #for index, row in df.iterrows():

    #Make variable for number of conditions
    compnum=args.cond

    #Make variable for working directory (stan and wrapper in same place)
    workdir = args.workdir

    c1_g1=args.c1_g1
    c1_g2=args.c1_g2
    c2_g1=args.c2_g1
    c2_g2=args.c2_g2
    comparison=args.compID
    design_c1=args.comparate_1
    design_c2=args.comparate_2

    print(c2_g1)
    print(comparison)
    print(design_c1)
    print(design_c2)

    row_list = []
    row_list = [c1_g1, c1_g2, c2_g1, c2_g2, comparison, design_c1, design_c2]

    ## remove empty if don't exist
    #row_list = [i for i in row_list if i]
    print(row_list)

    ## name of input file
    if design_c2 is False:
        comparison = design_c1
    elif design_c1 is False:
        comparison = design_c2
    else:
        comparison = comparison

    infileName = "bayesian_input_" + comparison + ".csv"

    infile=pd.read_csv(os.path.join(args.datafile, infileName))
    infile.set_index('FEATURE_ID')

    pre_headers=list(infile.columns.get_values())
    pre_headers_split=pre_headers[:4]
    pre_headers_split2=pre_headers[4:]

    row_list = [i for i in row_list if i]
    print('Printing row_list')
    print(row_list)

    for index,val in enumerate(row_list):
        c = 'c' + str(index + 1)
        val = ''.join(val)

        for i in range(len(pre_headers_split2)):
            if val in pre_headers_split2[i]:
                pre_headers_split2[i] = pre_headers_split2[i].replace(val, c)

    pre_headers_cat = pre_headers_split + pre_headers_split2
    print('printing pre_headers_cat')
    print(pre_headers_cat)
    infile.columns=pre_headers_cat


        ## c1 = M
        ## c2 = V
        ## g1 = tester or T
        ## g2 = line or L or Line

    infile.columns = pre_headers_cat

    ## add comparison column (last) 
    infile['comparison']=comparison
    
    datafile2 = args.datafile2 + comparison + '_temp.csv'

    infile.to_csv(datafile2, na_rep = 'NA', index=False)

    rout = comparison + '_r_out.csv'

    routput=os.path.join(args.routput, rout)
    print('Printing routput')
    print(routput)

    ## (2) Calls subprocess to run R script where args1 is the input csv and args2 is the output path for NBmodel.R##
    rscript = subprocess.call(['Rscript', args.subpath, datafile2, routput, compnum, workdir, args.iterations, args.warmup])

    ## (3) Format input from Rscript and get list of default header names, change headers back to actual comparates from c1 and c2
    df2 = pd.read_csv(routput)

    headers_all =list(df2.columns.values)
    print('printing headers_all')
    print(headers_all)

    for a in range(len(headers_all)):
        if 'c1' in headers_all[a]:
            headers_all[a] = headers_all[a].replace('c1', design_c1)
        if 'c2' in headers_all[a]:
            headers_all[a] = headers_all[a].replace('c2', design_c2)
    print('printing new headers_all')
    print(headers_all)

    df2.columns = headers_all
    
    ##Write to new CSV##
    outfile = 'bayesian_out_' + comparison + '.csv'
    output=os.path.join(args.output, outfile)

    df2.to_csv(output, na_rep = 'NA', index=False)

if __name__=='__main__':
    main()


