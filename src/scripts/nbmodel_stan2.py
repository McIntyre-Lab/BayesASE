
#! /usr/bin/Rscript
import subprocess
import os
import pandas as pd
import argparse


def getOptions():
    parser = argparse.ArgumentParser(description= "Run bayesian model")
    parser.add_argument('-collection_identifiers','--collection_identifiers',dest='collection_identifiers', action='store', required=True, help='Input original names [Required]')
    parser.add_argument('-collection_filenames','--collection_filenames',dest='collection_filenames', action='store', required=True, help='Input galaxy names [Required]')
    parser.add_argument("-datafile2","--datafile2",dest="datafile2",action="store",required=True,help="Provide temp path for created datafile with headers for Bayesian")
    parser.add_argument("-design","--design",dest="design",action="store",required=True,help="Design file containing sampleID names to analyze [TSV]")
    parser.add_argument("-cond","--cond", dest="cond", action="store", required=False, help="Number of conditions")
    parser.add_argument("-workdir","--workdir", dest="workdir", action="store", required=True, help="Path to R code")
    parser.add_argument("-routput","--routput", dest="routput", action="store", required=False, help="Optional R output file")
    parser.add_argument("-subpath","--subpath", dest="subpath", action="store", required=True, help="Bayesian R script subprocess path")
    parser.add_argument("-iterations","--iterations", dest="iterations", action="store", required=False, help="Optional number of iterations (default 100000)")
    parser.add_argument("-warmup","--warmup", dest="warmup", action="store", required=False, help="Optional number of warmup (default 10000)")
    parser.add_argument("-o","--output",dest="output",action="store", required=True,help="Output path for merged file[TSV]")
    args=parser.parse_args()
    return(args)

def main():
    args = getOptions()
    #pattern = re.compile(r'(?<=\').*(?=\')')
    identifiers = [i.strip() for i in args.collection_identifiers.split(",")]
    filenames = [i.strip() for i in args.collection_filenames.split(",")]
    input_dict = dict(zip(identifiers, filenames))
    
    ##(1) Parsing datafile to extract rows with sampleID specified in design file, set c1 and c2

    ##Standardized Paths##
    args.output = os.path.abspath(args.output)
    args.routput = os.path.abspath(args.routput)

    ## Read in design file as dataframe
    df = pd.read_csv(args.design, sep='\t')

    ## iterate over design file
    for index, row in df.iterrows():

        #Make variable for number of conditions
        compnum=args.cond

        #Make variable for working directory (stan and wrapper in same place)
        workdir = args.workdir

        df.set_index('Comparate_1')
        print(df)

        print('PRINTING data_row')
        print(row)
        comparison=row['compID']
        c1=row['Comparate_1']
        c2=row['Comparate_2']

        del row['compID']
        row = row.to_frame()

        row_list = row.values.tolist()

        ## remove empty if don't exist
        #row_list = [i for i in row_list if i]
        print(row_list)


        infileName = "bayesian_input_" + comparison

        infile=pd.read_csv(os.path.join(input_dict[infileName]),sep='\t')
        infile.set_index('FEATURE_ID')

        ## add comparison column (last)
        infile['comparison']=comparison

        datafile2 = args.datafile2 + '/' + comparison + '_temp'

        infile.to_csv(datafile2, na_rep = 'NA', index=False)

        rout = comparison + '_r_out'
        routput=os.path.join(args.routput, rout)

        ## (2) Calls subprocess to run R script where args1 is the input csv and args2 is the output path for NBmodel.R##
        rscript = subprocess.call(['Rscript', args.subpath, datafile2, routput, compnum, workdir, args.iterations, args.warmup])

        ## (3) Format input from Rscript and get list of default header names, change headers back to actual comparates from c1 and c2
        df2 = pd.read_csv(routput)

        headers_out =list(df2.columns.values)

        for a in range(len(headers_out)):
            if 'c1' in headers_out[a]:
                headers_out[a] = headers_out[a].replace('c1', c1)
            if 'c2' in headers_out[a]:
                headers_out[a] = headers_out[a].replace('c2', c2)

        df2.columns = headers_out

        ##Write to new CSV##
        outfile = 'bayesian_out_' + comparison
        output=os.path.join(args.output, outfile)

        df2.to_csv(output, na_rep = 'NA', index=False, sep='\t')

if __name__=='__main__':
    main()


