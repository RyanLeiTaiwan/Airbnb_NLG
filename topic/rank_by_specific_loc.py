from __future__ import unicode_literals
import spacy
import sys
import os
import csv
import operator
import numpy as np
import nltk
from collections import Counter, defaultdict
import pandas as pd
reload(sys)
sys.setdefaultencoding('utf8')

def output_selected_features():
        input_file = sys.argv[1]
        output_file = sys.argv[2]

        spacy.util.set_data_path("/Users/susie/git/") 
        nlp = spacy.load('en')
        f2 = open(output_file, 'w')
        df = pd.read_csv(input_file)
        print len(df)
        f2.write( "id|street|neighbourhood_cleansed|city|zipcode|country|desc_concat|best_sentence|entities\n") 
        for index, row in df.iterrows():
                desc = ""
                for column in ['neighborhood_overview', 'summary', 'space', 'transit']:
                        if not pd.isnull(row[column]):
                                desc += str(row[column])
                splitted_sen = nltk.sent_tokenize(desc)
                # first_loc_sent = ""
                # if not pd.isnull(row["neighborhood_overview"]):
                        # first_loc_sent = nltk.sent_tokenize(unicode(str(row["neighborhood_overview"]), "utf-8"))[0]
                # else:
                        # first_loc_sent = splitted_sen[0]
                max_count = 0
                best_sentence = ""
                entities = []
                for sentence in splitted_sen:
                        tmp = []
                        sentence = nlp(sentence.replace("|", "").decode('utf-8'))
                        count = 0
                        for ent in sentence.ents:
                                if ent.label_ in ['ORG', 'GPE', 'LOC', 'FAC']:
                                        count += 1
                                        tmp.append(str(ent.text))
                        if max_count < count:
                                best_sentence = str(sentence)
                                entities = tmp
                if best_sentence == "":
                        continue
                        # best_sentence = first_loc_sent
                new_line = str(row["id"])+"|" +str(row["street"])+"|" +str(row["neighbourhood_cleansed"])+"|" + \
                        str(row["city"])+"|" +str(row["zipcode"])+"|" +str(row["country"])+"|" +str(desc).replace("|","")+"|" +\
                        str(best_sentence).replace("|","")+"|" + str(', '.join(entities))
                f2.write( new_line + "\n") 
        f2.close()

output_selected_features()
