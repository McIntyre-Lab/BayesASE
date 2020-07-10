#!/usr/bin/env python3

#####  separate functions for simulated vs real data
#####  added additional argument to indicate whether dataset is a real or simulated dataset
#####  can specify if only want to run subset of rows in the design file

# Load packages
import argparse, csv, os, sys
import numpy as np
import pandas as pd


def getOptions():
    parser = argparse.ArgumentParser(description='Sum ase count tables element wise by sample ID provided in design file')
    parser.add_argument('-design','--design',dest='design', action='store', required=True, help='Design file containing fastq fqNames and sampleIDs [Required]')
    parser.add_argument('-sim','--sim',dest='sim', action='store', required=True, help='Assign to True if this is a simulation dataset, assign to False otherwise')
    parser.add_argument('-bed','--bed',dest='bed', action='store', required=False, help='File name (give the full path) of the bed file [Required]')
    parser.add_argument('-path','--path',dest='path', action='store', required=True, help='Path to directory containing ase_count_tables [Required]')
    parser.add_argument('-begin','--begin',dest='begin', action='store', required=False, help='Start point in design file [Optional]')
    parser.add_argument('-end','--end', dest='end', action='store', required=False, help='End point in design file [Optional]')
    parser.add_argument('-designdir','--designdir', dest='designdir', action='store', required=True, help='Output directory for design file')
    parser.add_argument('-out','--out', dest='out', action='store', required=True, help='Output directory for summed count table files [Required]')
    args = parser.parse_args()
    return(args)


##check that column names in count tables match expected
def headers_check(path,fname):
    df = pd.read_csv(os.path.join(path,fname))
    columns = ['FEATURE_ID','BOTH_EXACT', 'BOTH_INEXACT_EQUAL', 'SAM_A_ONLY_EXACT', 'SAM_B_ONLY_EXACT', 'SAM_A_EXACT_SAM_B_INEXACT', 'SAM_B_EXACT_SAM_A_INEXACT', 'SAM_A_ONLY_SINGLE_INEXACT', 'SAM_B_ONLY_SINGLE_INEXACT', 'SAM_A_INEXACT_BETTER', 'SAM_B_INEXACT_BETTER']
    headers = list(df)
    if headers != columns:
        print("ERROR: column headers in file " + fname + " are incorrectly named")
        sys.exit()

def sum_counts_sim(path,df_design,out):
    ##groupby sampleID; this allows us to select the correct count table files to sum together
    df_grouped = df_design.groupby('sampleID').agg(lambda x: x.tolist())

    ## count number of unique sampleIDs
    sampleID_count = len(df_grouped.index)
    print("Number of Sample IDs:")
    print(sampleID_count)

    ## Create list of filenames, iterate, put into a df
    for sampleID, filelist in df_grouped['fqName'].iteritems(): ##iterate grouped df using sampleID as index
        ddict = {}
        dfsum = pd.DataFrame(index=range(0),columns=['FEATURE_ID','BOTH_EXACT', 'BOTH_INEXACT_EQUAL', 'SAM_A_ONLY_EXACT', 'SAM_B_ONLY_EXACT', 'SAM_A_EXACT_SAM_B_INEXACT', 'SAM_B_EXACT_SAM_A_INEXACT', 'SAM_A_ONLY_SINGLE_INEXACT', 'SAM_B_ONLY_SINGLE_INEXACT', 'SAM_A_INEXACT_BETTER', 'SAM_B_INEXACT_BETTER'])
        dfsum = dfsum.set_index('FEATURE_ID')

        ## Iterate through the list of filenames in the filenames column
        for fqName in filelist:
            filename = 'ase_counts_' + fqName + '.csv'
            headers_check(path,filename)
            file = os.path.join(path,filename)
            ddict[filename] = pd.read_csv(file) ##we create a dictionary to store each count table file as a dataframe with their filename as the key
            ddict[filename] = ddict[filename].set_index('FEATURE_ID')
            dfsum = dfsum.add(ddict[filename], fill_value =  0)

            outfile = out +'/' + 'ase_sum_sim_counts_' + sampleID + '.csv' ##create outfile for summed matrix
            dfsum.to_csv(outfile)

def sum_counts_data(path,df_design,feature_lengths,out,designdir):
    
    ##groupby sampleID; this allows us to select the correct count table files to sum together
    df_grouped = df_design.groupby('sampleID').agg(lambda x: x.tolist())

    ## count number of unique sampleIDs
    sampleID_count = len(df_grouped.index)
    print("Number of Sample IDs:")
    print(sampleID_count)

    row = -1 ##this variable keeps track of which row in the design file (or subset design file) the filename would have been located in; we use this variable to extract the corresponding 
                  ##read length from the design file
    ## Create list of filenames, iterate, put into a df
    for sampleID, filelist in df_grouped['fqName'].iteritems(): ##iterate grouped df using sampleID as index
        ddict = {} 
        dfsum = pd.DataFrame(index=range(0),columns=['FEATURE_ID','BOTH_EXACT', 'BOTH_INEXACT_EQUAL', 'SAM_A_ONLY_EXACT', 'SAM_B_ONLY_EXACT', 'SAM_A_EXACT_SAM_B_INEXACT', 'SAM_B_EXACT_SAM_A_INEXACT', 'SAM_A_ONLY_SINGLE_INEXACT', 'SAM_B_ONLY_SINGLE_INEXACT', 'SAM_A_INEXACT_BETTER', 'SAM_B_INEXACT_BETTER'])
        dfsum = dfsum.set_index('FEATURE_ID')
 
        ## Iterate through the list of filenames in the filenames column
        for fqName in filelist:
            row += 1 
            filename = 'ase_counts_' + fqName + '.csv'
            headers_check(path,filename)
            file = os.path.join(path,filename)
            ddict[filename] = pd.read_csv(file) ##we create a dictionary to store each count table file as a dataframe with their filename as the key

            ##create columns for APN calculations
            ddict[filename]['total_reads_counted'] = ddict[filename]['BOTH_EXACT'] + ddict[filename]['BOTH_INEXACT_EQUAL'] + ddict[filename]['SAM_A_ONLY_EXACT'] + ddict[filename]['SAM_A_ONLY_SINGLE_INEXACT'] + ddict[filename]['SAM_A_EXACT_SAM_B_INEXACT'] + ddict[filename]['SAM_A_INEXACT_BETTER'] + ddict[filename]['SAM_B_ONLY_EXACT'] + ddict[filename]['SAM_B_ONLY_SINGLE_INEXACT'] + ddict[filename]['SAM_B_EXACT_SAM_A_INEXACT'] + ddict[filename]['SAM_B_INEXACT_BETTER'] 
            ddict[filename]['both_total'] = ddict[filename]['BOTH_EXACT'] + ddict[filename]['BOTH_INEXACT_EQUAL']
            readLength = df_design.iloc[row].loc['readLength'] ##get read length from design
            ddict[filename]['both x RL'] = ddict[filename]['both_total']*readLength

            ddict[filename]['total x RL'] = ddict[filename]['total_reads_counted']*int(readLength)
            ddict[filename] = ddict[filename].set_index('FEATURE_ID')
            dfsum = dfsum.add(ddict[filename], fill_value =  0)

            dfsum['APN_both'] = dfsum['both x RL']/feature_lengths
            dfsum['APN_total_reads'] = dfsum['total x RL']/feature_lengths
            dfout = dfsum.drop(['both x RL', 'total x RL', 'both_total', 'total_reads_counted'], axis=1) ##drop extra columns we no longer need

            outfile = out +'/' + 'ase_sum_counts_' + sampleID + '.csv' ##create outfile for summed matrix
            dfout.to_csv(outfile)

    ##create new design file with g1, g2, sampleID columns and add new empty columns for comparison 1 and comparison 2; new design file is output to the directory given in the -out argument
    ###if a subset of the design is given, the new design file will be created from that subset of the original design
    df_design['sample'] = df_design['sampleID'].str.rsplit('_', 1).str[0]
    print(df_design)
    df_drop = df_design.drop(['fqName','readLength', 'fqExtension', 'techRep'], axis=1)
    df_unique = df_drop.drop_duplicates()
    df_unique.to_csv(os.path.join(designdir,"df_ase_samcomp_summed.csv"), index=False)

def main():
    args = getOptions()

    ## Read in design file as dataframe
    df_design = pd.read_csv(args.design)

    ##check for optional begin/end argument; subset dataframe accordingly if arguments given
    if args.begin is not None and args.end is not None:
        ## reindex so pulling 'correct' rows
        begin = int(args.begin) -2
        end = int(args.end) -1
        df_design = df_design[begin:end]
        ##print what subset of the dataframe is being used
        begin = int(args.begin)
        print("begining on row " + str(begin))
        end = int(args.end)
        print("ending on row " + str(end))
    if args.sim == 'True':
        sum_counts_sim(args.path,df_design,args.out)
    elif args.sim== 'False':
        ##read in bed file and get feature lengths for APN calculations
        df_bed = pd.read_table(args.bed, names = ['col', 'start', 'end', 'FEATURE_ID'])
        df_bed =df_bed.set_index(['FEATURE_ID'])
        lengths = df_bed.end - df_bed.start
        feature_lengths = lengths.tolist()
        print(len(feature_lengths))
        sum_counts_data(args.path,df_design, feature_lengths,args.out,args.designdir)

if __name__=='__main__':
    main()
