from __future__ import unicode_literals
import spacy
import sys
import os
import operator
from collections import Counter, defaultdict
from findNameEntites import find_character_occurences
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
reload(sys)
sys.setdefaultencoding('utf8')

spacy.util.set_data_path("/Users/susie/git/") 
nlp = spacy.load('en')
city = sys.argv[1]
neighbourhoods_file = "./data/raw_data/" + city + "_neighbourhoods.csv"

neighbourhoods = []
with open(neighbourhoods_file, 'r') as f:
    for line in f:
        neighbourhoods.append(line.strip().split(',')[1])

neighbourhoods.pop(0)
location_entity_dict = defaultdict(Counter)

for neighbourhood in neighbourhoods:
    description = "./data/imtermidiate_data/" + city + "/" + neighbourhood + '.txt'
    if os.path.isfile(description):
        with open(description, 'r') as myfile:
            text = myfile.read()

        doc = nlp(text.decode('utf-8'))
        LocAndCnt = find_character_occurences(doc)[:5]
        for key, value in LocAndCnt:
            location_entity_dict[neighbourhood][key] = value

print location_entity_dict 

location_entity_df = pd.DataFrame.from_dict(dict(location_entity_dict), dtype=int)
location_entity_full_df = location_entity_df.fillna(value=0).astype(int)
# Show DF to console
heat_mask = location_entity_df.isnull()

hmap = sns.heatmap(location_entity_full_df, annot=True, fmt='d', cmap='YlGnBu', cbar=False, mask=heat_mask,  linewidths=1.5)

# Add features using the under the hood plt interface
#sns.axes_style('white')
#plt.title('Global Incidents by Terrorist group')
#plt.xticks(rotation=30)
#plt.yticks(rotation=30)
#axis.set_aspect('equal')
#
fontsize_pt = plt.rcParams['ytick.labelsize']
dpi = 72.27

# comput the matrix height in points and inches
matrix_height_pt = fontsize_pt * location_entity_full_df.shape[0]
matrix_height_in = matrix_height_pt / dpi

# compute the required figure height 
top_margin = 0.04  # in percentage of the figure height
bottom_margin = 0.04 # in percentage of the figure height
figure_height = matrix_height_in / (1 - top_margin - bottom_margin)


# build the figure instance with the desired height
fig, ax = plt.subplots(
        figsize=(6,figure_height), 
        gridspec_kw=dict(top=1-top_margin, bottom=bottom_margin))

# let seaborn do it's thing
ax = sns.heatmap(location_entity_full_df, ax=ax)
plt.xticks(rotation=30)
plt.yticks(rotation=30)
# save the figure
plt.savefig('/tmp/test.png')
plt.show()