import glob
import pandas as pd
import os
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction import DictVectorizer as DV

def prep_wage_tax_data(match_year, raw_data, stata_data, irs_filename, practice):
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
    :param practice: String. If "Yes" then only a toy version of the wage_data is created. If no, then all the wage data
    is merged to macth with the IRS data.
    :return: Returns two pandas dataframes. The first data frame is firm information for the non-profit firms from the
    wage data in the match year specified. The second data frame is firm information for the non-profit firms from the
    tax data in the match year specified.
    """

    # Importing the wage data for the specified match period
    final_data = pd.DataFrame()
    for year in xrange(match_year, match_year+2):
        appended_data = pd.DataFrame()
        year_s = str(year)
        if practice == "Yes":
            directory = raw_data + "/Wages " + year_s + "/practice/"
        else:
            directory = raw_data + "/Wages " + year_s
        print directory
        os.chdir(directory)
        for f in glob.glob("*.csv"):
            print f
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
    florida_data['employ_id'] = florida_data.index
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

    florida_data.loc[:, 'county'] = florida_data['county'].map(lambda x: x.strip(), na_action='ignore')
    florida_data.loc[:, 'county'] = florida_data['county'] + " County"
    florida_data = pd.merge(florida_data, name_fips_cw, how='outer', on='county')

    # Replacing missing fips codes
    florida_data.loc[florida_data['county']=='Miami-dade County', 'fips'] = "12086"
    florida_data.loc[florida_data['county'] == 'Saint Johns County', 'fips'] = "12109"
    florida_data.loc[florida_data['county'] == 'Saint Lucie County', 'fips'] = "12111"

    # Dropping data we don't need or that is missing
    florida_data.drop(['naics', 'legal', 'index', 'county'], axis=1, inplace=True)
    florida_data.dropna(inplace=True)
    florida_data.reset_index(inplace=True, drop=True)

    # Importing IRS tax data
    tax_path = raw_data + "IRS/soiSample/Quant_data/temp/" + irs_filename
    tax_data = pd.read_csv(tax_path, dtype={'state': str, 'zip': str, 'tot_num_empls': float,
                                            'comp_curr_ofcr_tot': float, 'oth_sal_wg_tot': float, 'taxpd': str,
                                            'ein': str},
                           usecols=['state', 'zip', 'tot_num_empls', 'comp_curr_ofcr_tot', 'oth_sal_wg_tot',
                                    'taxpd', 'ein'])
    tax_data = tax_data[tax_data['state'] == 'FL']
    tax_data['total_comp'] = tax_data['comp_curr_ofcr_tot'] + tax_data['oth_sal_wg_tot']
    tax_data.rename(columns={'tot_num_empls': 'total_emp'}, inplace=True)

    # Recoding tax year
    yr = str(match_year)[-2:]
    yr1 = str(match_year+1)[-2:]

    tax_data.loc[tax_data['taxpd'] == yr + '12', 'taxpd'] = '1'
    tax_data.loc[tax_data['taxpd'] == yr1 + '03', 'taxpd'] = '2'
    tax_data.loc[tax_data['taxpd'] == yr1 + '06', 'taxpd'] = '3'
    tax_data.loc[tax_data['taxpd'] == yr1 + '09', 'taxpd'] = '4'

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

    # Merging crosswalk with tax data and dropping observations with missing data
    tax_data = pd.merge(tax_data, zip_county_cw, how='inner', on='zip')
    tax_data.drop(['comp_curr_ofcr_tot', 'oth_sal_wg_tot', 'state', 'zip', 'pop10'], inplace=True, axis=1)
    tax_data.dropna(inplace=True)
    tax_data.reset_index(inplace=True, drop=True)

    # Outputting to csv's
    output_florida = raw_data + '/temp/' + 'florida_data_P' + practice + '.csv'
    output_tax = raw_data + '/temp/' + 'tax_data_P' + practice + '.csv'
    florida_data.to_csv(output_florida)
    tax_data.to_csv(output_tax)
    print "I'm done"
    # return florida_data, tax_data

def nearest_neighbors(wage_data_csv, tax_data_csv, tables_path, practice):
    """
    :param wage_data: File path to wage_data csv file
    :param tax_data: File path to tax_data csv file
    :return:
    """

    # Importing the csv files into dataframes
    wage_data = pd.read_csv(wage_data_csv, dtype={'ty1': float, 'ty2': float, 'ty3': float, 'ty4': float,
                                                  'total_emp': float, 'employ_id': str, 'fips': str})
    tax_data = pd.read_csv(tax_data_csv, dtype={'ein': str, 'taxpd': str, 'total_emp': float, 'total_comp': float,
                                                  'fips': str})

    # Putting an index column on wage and tax data
    wage_data.columns = ['ind'] + wage_data.columns[1:].tolist()
    tax_data.columns = ['ind'] + tax_data.columns[1:].tolist()

    # Finding neighbors for first tax year firms in tax data
    test_data = tax_data.loc[tax_data['taxpd']=='1', ['total_comp', 'total_emp']]
    train_data = wage_data.loc[:, ['ty1', 'total_emp']]
    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(train_data)
    distances, n1_ind = nbrs.kneighbors(test_data)
    n1_ind = np.squeeze(n1_ind)

    c1_match = wage_data.loc[np.squeeze(n1_ind), 'fips'].reset_index(drop=True) == tax_data.loc[tax_data['taxpd']=='1', 'fips'].reset_index(drop=True)
    round1_ind = n1_ind[np.array(c1_match)]
    wage_data['r1_bool'] = 0
    wage_data.loc[round1_ind, 'r1_bool'] = 1

    # Creating a dataframe with the matches
    matches = pd.DataFrame()
    matches = append_matches('1', c1_match, round1_ind, wage_data, tax_data, matches)
    print "Done with round 1"
    # Finding nearest neighbors for the third tax year firms in the data
    train3ind = wage_data.loc[wage_data['r1_bool']==0, 'ind']
    test_data = tax_data.loc[tax_data['taxpd']=='3', ['total_comp', 'total_emp']]
    train_data = wage_data.loc[train3ind, ['ty3', 'total_emp']]

    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(train_data)
    distances, n3_ind_temp = nbrs.kneighbors(test_data)
    n3_ind = train3ind[np.squeeze(n3_ind_temp)]
    c3_match = wage_data.loc[np.squeeze(n3_ind), 'fips'].reset_index(drop=True) == tax_data.loc[tax_data['taxpd']=='3', 'fips'].reset_index(drop=True)
    round3_ind = n3_ind[np.array(c3_match)]
    wage_data['r3_bool'] = 0
    wage_data.loc[round3_ind, 'r3_bool'] = 1  #The column r3 is a one if the firm is a match to a firm in the tax data.

    # Appending the matches
    matches = append_matches('3', c3_match, round3_ind, wage_data, tax_data, matches)
    print "Done with round3"
    # Finding nearest neighbors for the fourth tax year firms in the data.
    winners = wage_data['r1_bool'] + wage_data['r3_bool']
    train4ind = wage_data.loc[winners == 0, 'ind']
    test_data = tax_data.loc[tax_data['taxpd'] == '4', ['total_comp', 'total_emp']]
    train_data = wage_data.loc[train4ind, ['ty4', 'total_emp']]

    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(train_data)
    distances, n4_ind_temp = nbrs.kneighbors(test_data)
    n4_ind = train4ind[np.squeeze(n4_ind_temp)]
    c4_match = wage_data.loc[np.squeeze(n4_ind), 'fips'].reset_index(drop=True) == tax_data.loc[
        tax_data['taxpd'] == '4', 'fips'].reset_index(drop=True)
    round4_ind = n4_ind[np.array(c4_match)]
    wage_data['r4_bool'] = 0
    wage_data.loc[round4_ind, 'r4_bool'] = 1

    # Appending the matches
    matches = append_matches('4', c4_match, round4_ind, wage_data, tax_data, matches)
    matches.columns = ['indexw'] + matches.columns[1:5].tolist() + ['indext'] + matches.columns[6:].tolist()
    matches['tax_obs'] = tax_data.shape[0]
    output_path = tables_path + '/merge_soisampleTable1_P' + practice + '.csv'
    matches.to_csv(output_path)
    print "Done with round 4"
    return matches


def append_matches(tax_year, county_vec, round_vec, wage_data, tax_data, matches):
    """
    :param tax_year: tax year is a string of length 1 that equals 1,2, 3, or 4.
    :return: Appended data set of the matches
    """
    total_comp_str = 'ty' + tax_year
    tax_matches = tax_data.loc[tax_data['taxpd'] == tax_year, ['fips', 'total_comp', 'total_emp', 'ein', 'taxpd']][np.array(county_vec)]
    tax_matches.rename(columns={'fips': 'fipst', 'total_comp': 'total_compt', 'total_emp': 'total_empt'}, inplace=True)
    wage_matches = wage_data.loc[round_vec, ['fips', total_comp_str, 'total_emp', 'employ_id']]
    wage_matches.rename(columns={'fips': 'fipsw', total_comp_str: 'total_compw', 'total_emp': 'total_empw'}, inplace=True)
    temp = pd.concat([wage_matches.reset_index(), tax_matches.reset_index()], axis=1)
    matches = pd.concat([matches, temp], axis=0, ignore_index=True)
    return matches

# def analysis_ofmatches(output_file):
#     TODO: Fill in this code. right now i'm going to do this quick and dirty in stata.

def merge_soisample_func(match_year, raw_data, stata_data, tables_path, irs_filename, practice):
    # prep_wage_tax_data(match_year, raw_data, stata_data, irs_filename, practice)
    input_florida = raw_data + '/temp/' + 'florida_data_P' + practice + '.csv'
    input_tax = raw_data + '/temp/' + 'tax_data_P' + practice + '.csv'
    nearest_neighbors(input_florida, input_tax, tables_path, practice)


