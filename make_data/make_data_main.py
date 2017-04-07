# ----------------------------------------------------------
# Import functions
# ----------------------------------------------------------
from unique_firms import *
from merge_soisample import *
# ----------------------------------------------------------
# Parameters
# ----------------------------------------------------------
############################################################
# Paths
raw_data_path = "C:/Users/carli/Dropbox/projects/akm/dataRAW/"
stata_data_path = "../../dataSTATA"
############################################################
# ****Arguments for unique_firms, merge_soisample
match = 2010
tax_file = "10e0.csv"

# ****Arguments for unique_firms
year = 2010
ps=100

# ----------------------------------------------------------
# Main program
# ----------------------------------------------------------

# unique_firms_func(ps, year, ey, raw_data_path, stata_data_path)
merge_soisample_func(match, raw_data_path, stata_data_path, tax_file)

