import sys
import os
import csv
import operator
import numpy as np
import pandas as pd

def produce_inout_for_loc():
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


def produce_inout_for_space():
        data_file = sys.argv[1]
        input_file = sys.argv[2]
        output_file = sys.argv[3]   
        f_in = open(input_file, 'w')
        f_out = open(output_file, 'w')
        df = pd.read_csv(data_file, sep='|', error_bad_lines=False)
        df = df.replace(np.nan, '', regex=True)
        for index, row in df.iterrows():
                # id|street|neighbourhood_cleansed|city|country|name|bedrooms|bathrooms|property_type|room_type|desc_concat|best_sentence
                inputs = str(row["street"]).split(",")[0] + " " + str(row["neighbourhood_cleansed"]) + " " + \
                str(row["city"]) + " " + str(row["country"]) + " " + str(row["name"]) + ", " + str(row["bedrooms"]) + " bedrooms " + \
                str(row["bathrooms"]) + " bathrooms, " + str(row["property_type"]) + " " + str(row["room_type"])
                out = str(row["best_sentence"])
                f_out.write( out.lower() + "\n")
                f_in.write( inputs.lower() + "\n")
        f_in.close()
        f_out.close()

# produce_inout_for_loc()
produce_inout_for_space()