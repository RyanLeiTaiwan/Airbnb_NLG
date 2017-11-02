import sys
import os
import csv
import operator
import numpy as np
import pandas as pd

def produce_inout():
        data_file = sys.argv[1]
        input_file = sys.argv[2]
        output_file = sys.argv[3]   
        f_in = open(input_file, 'w')
        f_out = open(output_file, 'w')
        df = pd.read_csv(data_file, sep='|', error_bad_lines=False)
        df = df.replace(np.nan, '', regex=True)
        for index, row in df.iterrows():
                inputs = str(row["street"]).split(",")[0] + " " + str(row["neighbourhood_cleansed"]) + " " + \
                str(row["city"]) + " " + str(row["zipcode"]) + " " + str(row["country"]) + " " + str(row["entities"])
                out = str(row["best_sentence"])
                f_out.write( out.lower() + "\n")
                f_in.write( inputs.lower() + "\n")
        f_in.close()
        f_out.close()

produce_inout()