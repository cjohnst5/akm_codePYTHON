# ----------------------------------------------------------
# Import functions
# ----------------------------------------------------------
from merge_sample_and_trend import *

# ----------------------------------------------------------
# Parameters
# ----------------------------------------------------------
raw_data_path = "../../dataRAW"
stata_data_path = "../../dataSTATA"
year = 2010

# ----------------------------------------------------------
# Main program
# ----------------------------------------------------------
merge_sample_and_trend_func(raw_data_path, stata_data_path, year)