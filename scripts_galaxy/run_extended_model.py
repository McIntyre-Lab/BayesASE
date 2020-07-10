#! /usr/bin/Rscript
#import rpy2.robjects as robjects
#import pandas as pd
import subprocess
import os
import pandas as pd
import argparse
import re

parser = argparse.ArgumentParser(description= "merges two .csv files on two common columns")
parser.add_argument("-datafile","--datafile",dest="datafile",action="store",required=True,help="Provide path for input datafile [CSV]")
#parser.add_argument("-subpath","--subpath", dest="subpath", action="store", required=True, help="Bayesian R script subprocess path")
parser.add_argument("-compid","--compid",dest="compid",action="store", required=True,help="Output path for merged file[CSV]")
parser.add_argument("-cond","--cond",dest="cond",action="store", required=True,help="Output path for merged file[CSV]")
parser.add_argument("-workdir","--workdir",dest="workdir",action="store", required=True,help="Output path for merged file[CSV]")
parser.add_argument("-o","--output",dest="output",action="store", required=True,help="Output path for merged file[CSV]")
args = parser.parse_args()


##Standardized Paths##
args.output = os.path.abspath(args.output)
args.datafile = os.path.abspath(args.datafile)
r_script_path = os.path.join(localpath, "NBmodel.R")

## Set outfile name
bayesian_out = 'bayesian_out_' + args.compid + '.csv'
output=os.path.join(args.output, bayesian_out)

datafile = args.datafile

## Set number of comparates to be analyzed
compnum = args.cond

## Make variable of working directory
workdir = args.workdir

## (1) Call subprocess to run R script where args1 is the input csv and args2 is the output path for NBmodel.R##
rscript = subprocess.call(['Rscript', r_script_path, datafile, output, compnum, workdir])

