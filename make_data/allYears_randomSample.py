import numpy as np
import pandas as pd
import os

#Steps
#=====Modify these
#Input file name
inputFile = "makeAllMoversV3_PS100_data.dta"
#Output fileName
outputFile = "makeAllMoversV3_PS10_python_data.csv"
#===============
#Directories
dir_path = os.getcwd()
print (dir_path)
dir_path_back = dir_path.rsplit('\\',1)[0]
dir_path_input = dir_path_back + "/dataSTATA/" + inputFile
dir_path_output = dir_path_back + "/dataSTATA/" + outputFile
print (dir_path_input)


#1. Load all the years data
#allYears = pd.read_stata(dir_path_input)
allYears = pd.read_stata('../dataSTATA/makeAllMoversV3_PS100_data.dta')
worker_id = allYears.worker_id.unique()
print ("Worker id shape")
print (worker_id.shape)
sample_worker_id = pd.Series(worker_id).sample(int(len(worker_id)/10))
subsetAllYears = allYears[allYears['worker_id'].isin(sample_worker_id)]
print ("Subset Length") 
print (len(subsetAllYears))
#subsetAllYears.to_csv(dir_path_output, sep =',')
subsetAllYears.to_csv("../dataSTATA/makeAllMoversV3_PS10_python_data.csv", sep =',')
print ("Done")
#2. Get unique social security identifiers
#3. Randomly sample unique identifiers
#4. Merge the identifiers back onto all your data
#5. Done with random sample. 