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

        keywords = ['property', 'apartment', 'apt', 'house', 'home', 'guesthouse', 'townhouse', 'condo', 'condominium', 'hostel', 'hotel', 'suite', 'bed', 'breakfast', 'dorm', 'cottage', 'floor', 'private', 'shared', 'mixed', 'family', 'room', 'bedroom', 'bathroom', 'spacious', 'roomy', 'cozy', 'comfortable', 'quiet', 'queen', 'king', 'sized', 'acre', 'sqft', 'bath', 'square', 'feet', 'space', 'br']
        spacy.util.set_data_path("/Users/susie/git/") 
        f2 = open(output_file, 'w')
        df = pd.read_csv(input_file)
        print len(df)
        f2.write( "id|street|neighbourhood_cleansed|city|country|name|bedrooms|bathrooms|property_type|room_type|desc_concat|best_sentence\n") 
        for index, row in df.iterrows():
                desc = ""
                for column in ['summary', 'neighborhood_overview', 'space', 'transit']:
                        if not pd.isnull(row[column]):
                                desc += str(row[column])
                splitted_sen = nltk.sent_tokenize(desc)
                # first_space_sent = ""
                # if not pd.isnull(row["space"]):
                #         first_space_sent = nltk.sent_tokenize(unicode(str(row["space"]), "utf-8"))[0]
                # else:
                #         first_space_sent = splitted_sen[0]
                max_count = 0
                best_sentence = ""
                for sentence in splitted_sen:
                        sentence = sentence.strip()
                        count = 0
                        for word in keywords:
                                if word in sentence:
                                        count += 1

                        if max_count < count:
                                best_sentence = str(sentence)
                if best_sentence == "":
                        continue
                new_line = str(row["id"]).replace("|","")+"|" +str(row["street"]).replace("|","")+"|" +str(row["neighbourhood_cleansed"]).replace("|","")+"|" + \
                        str(row["city"]).replace("|","")+"|" +str(row["country"]).replace("|","")+"|" +str(row["name"]).replace("|","")+"|" +str(row["bedrooms"])+\
                        "|"+str(row["bathrooms"])+"|"+str(row["property_type"]).replace("|","")+"|" +str(row["room_type"]).replace("|","")+"|"+\
                        str(desc).replace("|","").replace("|","")+"|"+str(best_sentence).replace("|","")
                f2.write( new_line + "\n") 
        f2.close()

output_selected_features()
