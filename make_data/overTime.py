import pandas as pd
import numpy as np
def over_time_func(input_path, output_path, percent_sample, version, movers_type, naics, num_ind):

    #Setting up directories
    ps_word = percent_sample.replace(".", "")
    print ps_word
    input_file = input_path + "/overTimeMedWageYear" + version + "_PS" + ps_word + "_MT" + movers_type + "_N" + naics + ".csv"
    output_file = output_path + "/overTimeTable3" + version + "_PS" + ps_word + "_MT" + movers_type + "_N" + naics
    #Import data
    florida_data = pd.read_csv(input_file)
    print len(florida_data), florida_data.columns
    
#     Finding total number of workers
    p_table = pd.pivot_table(florida_data, index=['year', 'month', naics], columns=['non_profit'])
    p_table.reset_index(level=['year', 'month', naics], inplace=True)
    print p_table.index
    p_table['ind_count_total'] = p_table['indCount'][0] + p_table['indCount'][1]

#   Finding percentage of np and fp workers
    p_table['ind_percent_fp'] = p_table['indCount'][0] / p_table['ind_count_total']
    p_table['ind_percent_np'] = p_table['indCount'][1] / p_table['ind_count_total']

    # Keeping year and month we are interested in
    p_table = p_table[((p_table['year'] == 2004) & (p_table['month'] == 3)) |((p_table['year'] == 2012) & (p_table['month'] == 3))]
    del p_table['month']
    p_table.columns = ['year', naics, 'indCount0', 'indCount1', 'medWageYear0', 'medWageYear1', 'ind_count_total', 'ind_percent_fp', 'ind_percent_np']
    p_table = p_table.pivot_table(index=naics, columns=['year'])

    # **Finding industries with top ten non profit workers and exporting results

    for i in [2004, 2012]:
        p_table.sort_values(by=('indCount1', i), ascending=0, inplace=True)
        results = p_table.ix[:, [('ind_percent_np', i), ('ind_percent_fp', i)]]
        results = results.head(n=num_ind)
        results.reset_index(inplace=True)
        print results.index
        yr = str(i)
        results.to_csv(output_file+yr+".csv")

    return p_table

#Defining parameters to pass to our function
ip = "../dataSTATA"
op = "../tables"
ps = "10"
vs = "V3"
movers_type = "All"
naics = "naics_3d"
num_ind = 10
table1 = over_time_func(ip, op, ps, vs, movers_type, naics, num_ind)
print "Hello"