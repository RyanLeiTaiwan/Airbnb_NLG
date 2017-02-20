import csv
import sys
from collections import defaultdict
import os

reload(sys)
sys.setdefaultencoding('utf8')

columns = defaultdict(list) # each value in each column is appended to a list
city = sys.argv[1]

details_file = "./data/raw_data/" + city + "_details.csv"
neighbourhoods_file = "./data/raw_data/" + city + "_neighbourhoods.csv"


with open(details_file) as f:
    reader = csv.DictReader(f) # read rows into a dictionary format
    for row in reader: # read a row as {column1: value1, column2: value2,...}
        for (k,v) in row.items(): # go over each column name and value 
            columns[k].append(v.decode('string_escape')) # append the value into the appropriate list
                                 # based on column name k

text = columns['neighborhood_overview']
neighbourhood = columns['neighbourhood_cleansed']

mapping = dict()
mapping
for i in xrange(len(text)):
	if text[i] != None:
		mapping[text[i]] = neighbourhood[i]		

grouped_data = defaultdict(list)

for key, value in sorted(mapping.iteritems()):
    grouped_data[value].append(key)

# create a folder
new_folder = "./data/imtermidiate_data/" + city
if not os.path.exists(new_folder):
    os.makedirs(new_folder)

for key in grouped_data:
	filename = key + '.txt'
	with open(os.path.join(new_folder, filename), 'wb') as temp_file:
	    temp_file.write("\n".join(grouped_data[key]))