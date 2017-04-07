import pandas as pd
import numpy as np
print "Hello"

def acsCompareFunc(inputPath, outputPath, numIndustries, version, percentSample, naics):
    """
    This function finds the top 10 non profit industries in the ACS data and exports tables to excel with
    the top 10 industry NAICS codes and percentage share of the market.
    :param inputPath:
    :param outputPath:
    :param numIndustries:
    :param version:
    :param percentSample:
    :param naics:
    :return:
    """
    #Setting up directories
    ps_word = percentSample.replace(".", "")
    inputFile = inputPath + "/ACS/PUM_2005_2014.csv"
    outputFile = outputPath 
    #Import data
    acsData = pd.read_csv(inputFile)
    print len(acsData), acsData.columns

    #Number of workers in each industry, by year
    ttl_wrkrs = pd.crosstab(acsData[naics], acsData['year'])
    print "Next"
    #Number of workers in each industry, by year, split on nonprofit
    np_wrkrs = pd.crosstab([acsData['non_profit_acs'], acsData[naics]], acsData['year'])

    #Find top 10 non-profit industries in 2005 and 2012
    cTab2005 = pd.DataFrame(np_wrkrs.loc[1][2005].copy())
    cTab2005.sort_values(by = 2005, ascending = 0, inplace= True)
    # cTab2005.drop(cTab2005.index[numIndustries:], inplace = True)
    print cTab2005, 'cTab2005'

    cTab2012 = pd.DataFrame(np_wrkrs.loc[1][2012].copy())
    cTab2012.sort_values(by = 2012, ascending = 0, inplace= True)
    # cTab2012.drop(cTab2012.index[numIndustries:], inplace = True)
    print cTab2012, "Ctab2012"
    
    #Find percentages
    cTab2005 =cTab2005.join(ttl_wrkrs[2005], rsuffix = "total")
    cTab2012 = cTab2012.join(ttl_wrkrs[2012], rsuffix = "total")
    print cTab2005.columns
    cTab2005['percent'] = cTab2005["2005"]/cTab2005["2005total"]
    del cTab2005['2005']
    del cTab2005['2005total']
    cTab2005.columns = ['ind_percent_np']
    print cTab2012.columns
    cTab2012['percent'] = cTab2012["2012"] / cTab2012["2012total"]
    del cTab2012['2012']
    del cTab2012['2012total']
    cTab2012.columns = ['ind_percent_np']

    #Clean up table and export it to latex and excel
    cTab2005.to_csv(outputPath+"/acsCompareTable2"+version+"_PS"+ps_word+"_N"+naics+"2005.csv")
    cTab2012.to_csv(outputPath+"/acsCompareTable2"+version+"_PS"+ps_word+"_N"+naics+"2012.csv")

    return acsData, cTab2005, cTab2012

#Defining function arguments
dataRAW = "../dataRAW"
output = "../tables"
numInd = 10
version = "V3"
perSamp = "10"
naics = "naics_3d_acs"
print "Here we are"
acsDat, cTab2005, cTab2012 = acsCompareFunc(dataRAW, output, numInd, version, perSamp, naics)
