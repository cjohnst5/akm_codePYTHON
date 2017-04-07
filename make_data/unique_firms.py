import pandas as pd
import numpy as np
import string

def unique_firms_func(percent_sample, begin_year, end_year, raw_data, stata_data):
    """
    This function finds firms which are the only firms in their naics code county group in the IRS data (core trend)
    and the UI data (social_data).
    It then merges data on the unique firms together from the two data sets.

    This is unfinished because I don't think this is a great way to match the data.

    :param percent_sample: float that indicates the percent sample to create from all the wage records
            1.0 means 1 percent
    :param begin_year: Integer. First year for which we want to clean up data
    :param end_year: Integer. Last year for which we want to clean data
    :return:
    """

    # Formatting file names
    year_str = str(begin_year)
    file_name1 = raw_data + "/social.dta"
    file_name2 = raw_data + "/IRS/npCoreFiles/CoreTrendPC" + year_str + ".csv"
    file_name3 = raw_data + "/countyNameFipsCrosswalk.csv"

    # Loading the data
    # social_data = pd.read_stata(file_name1, columns=['employ_id', 'county', 'naics'])
    trend_file = pd.read_csv(file_name2, usecols = ['ein', 'naics', 'fips'], dtype={'ein':np.str_, 'naics':np.str_, 'fips':np.str_},
                             na_values={'fips': '.'})
    crosswalk = pd.read_csv(file_name3)

    # Cleaning up crosswalk
    crosswalk.dropna(inplace=True)
    crosswalk.reset_index(drop=True, inplace=True)
    crosswalk['fips'] = crosswalk['fips'].astype(int)
    crosswalk['county'] = crosswalk['county'].map(lambda x: string.replace(x, ' County', ''))

    #Cleaning up trend_file
    trend_file.dropna(inplace=True)
    trend_file['fips'] = trend_file['fips'].map(lambda x: string.replace(x, '12', ''))
    trend_file['fips'].astype(float)
    trend_file['fips'] = trend_file['fips'].astype(int)

    # Find county naics combos that only have one firm in them
    social_data['group_counts'] = social_data.groupby(['county','naics'], as_index=False)['employ_id'].transform(np.size)
    social_data = social_data[social_data['group_counts']==1]
    trend_file['group_counts'] = trend_file.groupby(['fips', 'naics'], as_index=False)['ein'].transform(np.size)
    trend_file = trend_file[trend_file['group_counts']==1]

    print "Hello"