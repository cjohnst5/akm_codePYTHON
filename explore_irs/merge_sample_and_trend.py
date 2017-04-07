import pandas as pd
def merge_sample_and_trend_func(raw_data, stata_data, year):
    """
    This function merges the data from the SOIS sample to the core trend file data. I thought I would need NAICS codes
    on some of the core trend organizations. I ended up not finishing this function because eventually I didn't need the
    NAICS codes.
    :param raw_data: String that is the file path to the raw data folder eg "C:Carla/project1/dataRAW"
    :param stata_data: String that is the file path to the stata data folder
    :param year: 4-digit integer of the year of data we want to merge
    :return: Returns ...
    """
    print "Inside function"
    # Import Sample SOI IRS file
    year_str = str(year)
    if year <= 2010:
        file_name = year_str[-2:] + "eo.dta"
    else:
        file_name = "eo" + year_str + ".dta"

    input_file = raw_data + "/IRS/soiSample/Quant_data/temp/" + file_name
    soi_sample = pd.read_stata(input_file, columns=["ein"])
    soi_sample['ein'] = soi_sample['ein'].astype(int)

    # print soi_sample.shape
    print "I'm in here"
    # Import Core trend file
    input_file = raw_data + "/IRS/npCoreFiles/CoreTrendPC" + year_str + ".csv"
    trend_file = pd.read_csv(input_file, usecols = ['ein', 'naics'])
    # Merge core trend file with sample soi irs file
    soi_sample = soi_sample.merge(trend_file, how='left', on='ein')
    print "Number of NaNs"
    print sum(pd.isnull(soi_sample['naics']))
    print "Sample is done"





