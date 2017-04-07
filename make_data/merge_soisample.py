import glob
import pandas as pd
import os
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction import DictVectorizer as DV

def prep_wage_tax_data(match_year, raw_data, stata_data, irs_filename):
    """
    This function matches the UI wage data with the IRS tax data for nonprofit firms. It saves the merged
    data as a csv file. it doesn't return anything.

    :param begin_year: integer. First year we want to merge with IRS data. For example, if the year is 2010
    then we use the calendar year 2010 to calculate total number of employees and the fiscal year indicated on
    the 2010 990 form to calculate total compensation. We would use these numbers to merge the 2010 soi sample data to
    the UI data for the years 2010-2011 (if the fiscal year ends in 2011).
    :param end_year: Integer. Last year we want to merge with IRS data
    :param raw_data: String. File path to the raw data folder.
    :param stata_data: String. File path to the stata data folder.
    :param irs_filename: String. File name of the IRS data we need to use to match to the wage data. I'm using this
    the data filenames differ across years, so we can't specify the file name purely by knowing the match year.
    """

    # Importing the wage data for the specified match period
    print "I'm inside"
    final_data = pd.DataFrame()
    for year in xrange(match_year, match_year+2):
        appended_data = pd.DataFrame()
        year_s = str(year)
        directory = raw_data + "/Wages " + year_s + "/practice/"
        os.chdir(directory)
        for f in glob.glob("*.csv"):
            # Read in data file
            df = pd.read_csv(f, dtype={'employ_id': str, 'worker_id': str, 'year': float, 'month': float, 'wages': float})
            # Dropping nonsense workers and missing values
            df = df[(df['worker_id']!='00000000000000000000')]
            df.dropna(inplace=True)
            # Aggregate total compensation and total number of workers in each file
            grouped = df.groupby('employ_id')
            grouped_agg = grouped.agg({'year': np.mean, 'month': np.mean, 'wages': np.sum})
            group_size = grouped.size()
            group_size.rename('total_emp', inplace=1)
            grouped_agg = grouped_agg.join(group_size)
            # Append to existing data
            appended_data = appended_data.append(grouped_agg)

        # Final aggregation for the year and quarter
        appended_data['employ_id'] = appended_data.index
        year_data = appended_data.groupby(['employ_id', 'year', 'month']).agg({'wages': np.sum, 'total_emp': np.sum})

        # Append data for each year
        final_data = final_data.append(year_data)

    # Adding up total number of employees by year
    total_emp = final_data.groupby(level=['employ_id', 'year']).agg({'total_emp': np.sum})
    total_emp = total_emp[total_emp.index.get_level_values(1) == match_year]
    total_emp = total_emp['total_emp']
    total_emp.index = total_emp.index.droplevel(1)

    # Adding up wages for four different potential tax years
    quarter_wages = final_data['wages'].unstack([1, 2])
    quarter_wages['ty1'] = quarter_wages[2010, 3] + quarter_wages[2010, 6] + quarter_wages[2010, 9] + \
                            quarter_wages[2010, 12]
    quarter_wages['ty2'] = quarter_wages[2010, 6] + quarter_wages[2010, 9] + quarter_wages[2010, 12] + \
                            quarter_wages[2011, 3]
    quarter_wages['ty3'] = quarter_wages[2010, 9] + quarter_wages[2010, 12] + quarter_wages[2011, 3] + \
                           quarter_wages[2011, 6]
    quarter_wages['ty4'] = quarter_wages[2010, 12] + quarter_wages[2011, 3] + quarter_wages[2011, 6] + \
                           quarter_wages[2011, 9]
    quarter_wages = quarter_wages[['ty1', 'ty2', 'ty3', 'ty4']]
    quarter_wages.columns = quarter_wages.columns.droplevel(1)

    # Importing firm level data from Florida records
    social = pd.read_csv(raw_data + "/social.csv", dtype={'employ_id': str, 'county': str, 'naics': str, 'legal': str},
                         usecols=['employ_id', 'county', 'naics', 'legal'])
    social.set_index('employ_id', inplace=True, drop=True)
    # Assigning fips codes to counties

    # Merging firm level data with aggregated wage records and employment records
    florida_data = pd.concat([social, quarter_wages, total_emp], axis=1, join='inner')

    # Keeping only nonprofits
    florida_data['legal'] = florida_data['legal'].map(lambda x: x.replace("C", "").strip(), na_action='ignore')
    florida_data = florida_data[florida_data['legal']=='Not-for-Profit']

    # Merging with county fips codes
    crosswalk_path = raw_data + "crosswalks/countyNameFipsCrosswalk.csv"
    name_fips_cw = pd.read_csv(crosswalk_path, dtype={'county': str, 'fips': str})
    name_fips_cw.dropna(inplace=True)
    name_fips_cw.reset_index(inplace=True)
    name_fips_cw['county'] = name_fips_cw['county'].map(lambda x: x.strip())
    length1 = name_fips_cw['fips'].map(lambda x: len(x) == 1)
    name_fips_cw.loc[length1, 'fips'] = "00" + name_fips_cw.loc[length1, 'fips']
    length2 = name_fips_cw['fips'].map(lambda x: len(x) == 2)
    name_fips_cw.loc[length2, 'fips'] = "0" + name_fips_cw.loc[length2, 'fips']
    name_fips_cw['fips'] = '12' + name_fips_cw['fips']

    florida_data['county'] = florida_data['county'].map(lambda x: x.strip(), na_action='ignore')
    florida_data['county'] = florida_data['county'] + " County"
    florida_data = pd.merge(florida_data, name_fips_cw, how='outer', on='county')

    # Replacing missing fips codes
    florida_data.loc[florida_data['county']=='Miami-dade County', 'fips'] = "12086"
    florida_data.loc[florida_data['county'] == 'Saint Johns County', 'fips'] = "12109"
    florida_data.loc[florida_data['county'] == 'Saint Lucie County', 'fips'] = "12111"

    # Dropping data we don't need and getting county dummies
    florida_data.drop(['naics', 'legal', 'index', 'county'], axis=1, inplace=True)
    florida_data.dropna(inplace=True)
    train_data = pd.get_dummies(florida_data, columns=['fips'])
    train_data.drop(['ty1', 'ty2', 'ty3', 'ty4'], inplace=True, axis=1)

    # Importing IRS tax data
    tax_path = raw_data + "IRS/soiSample/Quant_data/temp/" + irs_filename
    tax_data = pd.read_csv(tax_path, dtype={'state': str, 'zip': str, 'tot_num_empls': float,
                                            'comp_curr_ofcr_tot': float, 'oth_sal_wg_tot': float},
                           usecols=['state', 'zip', 'tot_num_empls', 'comp_curr_ofcr_tot', 'oth_sal_wg_tot'])
    tax_data = tax_data[tax_data['state'] == 'FL']
    tax_data['total_comp'] = tax_data['comp_curr_ofcr_tot'] + tax_data['oth_sal_wg_tot']
    tax_data.rename(columns={'total_num_empls': 'total_emp'}, inplace=True)

    # Importing crosswalk
    crosswalk_path = raw_data + "crosswalks/zcta5_county_florida.csv"
    zip_county_cw = pd.read_csv(crosswalk_path, dtype={'state': str, 'zcta5': str, 'county': str},
                                usecols=['zcta5', 'county', 'pop10'])
    zip_county_cw.rename(columns={'zcta5': 'zip', 'county': 'fips'}, inplace=True)

    # Some zipcodes cross county lines, so we assign them to the county the have the most population in
    max_pop = zip_county_cw.groupby('zip').aggregate(np.max)
    max_pop['zip'] = max_pop.index
    max_pop.drop('fips', inplace=True, axis=1)
    zip_county_cw = pd.merge(zip_county_cw, max_pop, how='inner', on=['zip', 'pop10'])

    # Merging crosswalk with tax data and getting county dummies
    tax_data = pd.merge(tax_data, zip_county_cw, how='inner', on='zip')
    tax_data.drop(['comp_curr_ofcr_tot', 'oth_sal_wg_tot', 'state', 'zip', 'pop10'], inplace=True, axis=1)
    test_data = pd.get_dummies(tax_data, columns=['fips'])
    test_data.drop('total_comp', axis=1, inplace=True)

    # Filling in missing county columns. Hmm. This isn't generalizable. I'll think about this more.
    test_data['fips_12013'] = 0
    test_data['fips_12023'] = 0
    test_data['fips_12029'] = 0
    test_data['fips_12037'] = 0
    test_data['fips_12039'] = 0
    test_data['fips_12041'] = 0
    test_data['fips_12043'] = 0
    test_data['fips_12047'] = 0
    test_data['fips_12067'] = 0
    test_data['fips_12075'] = 0
    test_data['fips_12119'] = 0
    test_data['fips_12123'] = 0
    test_data['fips_12125'] = 0
    test_data['fips_12131'] = 0

    train_data['fips_12027'] = 0
    train_data['fips_12077'] = 0
    train_data['fips_12093'] = 0

    test_data.sort_index(axis=1, inplace=True)
    train_data.sort_index(axis=1, inplace=True)






    print "All done"



