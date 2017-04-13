# ----------------------------------------------------------
# Import functions
# ----------------------------------------------------------
# from unique_firms import *
from merge_soisample import *
# ----------------------------------------------------------
# Parameters
# ----------------------------------------------------------
############################################################
# Paths
# Home desktop
raw_data_path = "C:/Users/Daniel and Carla/Dropbox/projects/akm/dataRAW/"
stata_data_path = "C:/Users/Daniel and Carla/Dropbox/projects/akm//dataSTATA"

# School desktop
raw_data_path = "C:/Users/carli/Dropbox/projects/akm/dataRAW/"
stata_data_path = "C:/Users/carli/Dropbox/projects/akm//dataSTATA"
tables_path = "C:/Users/carli/Dropbox/projects/akm//tables"

# # EML account
# raw_data_path = "/scratch/public/carlajohnston/compDiff/dataRAW/"
# figures_path = "/scratch/public/carlajohnston/compDiff/figures/"
# stata_data_path = "/scratch/public/carlajohnston/compDiff/dataSTATA/"
# code_stata_path = "/scratch/public/carlajohnston/compDiff/codeSTATA/"
# tables_path = "/scratch/public/carlajohnston/compDiff/tables/"

############################################################
# ****Arguments for unique_firms, merge_soisample
match = 2010
tax_file = "10e0.csv"

# ****Arguments for unique_firms
year = 2010
ps=100

# ****Arguments for merge_soisample
practice = ''
# ----------------------------------------------------------
# Main program
# ----------------------------------------------------------

# unique_firms_func(ps, year, ey, raw_data_path, stata_data_path)
merge_soisample_func(match, raw_data_path, stata_data_path, tables_path, tax_file, practice)

