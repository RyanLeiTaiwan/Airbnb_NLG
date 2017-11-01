import nltk
import re
import string
import pandas as pd
import argparse
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize

def build_parser():
    parser = argparse.ArgumentParser(description='Select transit related data and description')
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='The input csv file'
    )
    return parser

def complete_data(row, data_cols):
    build_string = []
    for col in data_cols:
	value = getattr(row, col)
	if value is np.nan:
                continue
        if col == "street":
            build_string.append(value.split(",")[0])
        else:
            build_string.append(value)
    return ' , '.join(build_string) 
   
def complete_description(row, desc_cols):
    build_string = []
    for col in desc_cols:
	value = getattr(row, col)
	if value is np.nan:
		continue
        build_string.append(value.strip())
    return ' '.join(build_string)
    
if __name__ == '__main__':
    parser = build_parser()
    n = parser.parse_args()
    stemmer = WordNetLemmatizer()
    desc_cols = ["transit", "summary", "neighborhood_overview"]
    data_cols = ["street", "neighbourhood_cleansed", "city", "zipcode", "country"]
    keywords = ["commute", "bus", "station", "transit", "train", "metro", "railway", "transport", "subway", "ferry"]
    tot_cnt = 0
    
    infile = n.input
    file_type = infile.split('.')[0]
    data_file = open(file_type + "_transit.data", "wb")
    desc_file = open(file_type + "_transit.desc", "wb")
    # record the hostid and the line number
    id_map = open(file_type + "_transit.id", "wb")
    
    df = pd.read_csv(infile)
    for idx, row in df.iterrows():
        data_list = []
        
        desc_trans = ""
        sent_cnt = 0
        
        data_line = complete_data(row, data_cols)
        data_line = re.sub("\s+"," ",data_line)
        
        description = complete_description(row, desc_cols)
	# sent_tokenize needs unicode
        sents = sent_tokenize(description.decode('utf8'))
        
        for sent in sents: 
            desc_list = []
            match_cnt = 0
            desc_tokens = word_tokenize(sent)
            for word in desc_tokens:
                end_punct = []
		if len(word) == 0:
			continue
                word = word.lower()
		# deal with the case "word," and ",word"
                while len(word) > 0 and word[0] in string.punctuation:
                    start = word[0]
                    desc_list.append(start)
                    word = word[1:]
                while len(word) > 0 and word[-1] in string.punctuation:
                    end = word[-1]
                    word = word[:-1]
                    end_punct.append(end)

		if len(word) > 0:
                	desc_list.append(word)    
		if len(end_punct) > 0:
			end_punct.reverse()
                	desc_list.extend(end_punct)

                # the criteria to decide whether to include this sentence
                try: 
                    stem = stemmer.lemmatize(word)
                    if stem in keywords:
                        match_cnt += 1
		except:
		    pass

            cur_desc = " ".join(desc_list)
            cur_desc = re.sub("\s+"," ",cur_desc)
           
            if match_cnt > 0:
                sent_cnt += 1
                if sent_cnt > 1 and len(desc_trans) + len(cur_desc) > 300:
		    break
                desc_trans = desc_trans + cur_desc + " "
                if sent_cnt == 3:
                    break
                 
        if len(desc_trans) > 20:
            desc_file.write(desc_trans.encode('utf8') + "\n")
            data_file.write(data_line + "\n")
            id_map.write(str(row["id"]) + "\n")
            
        if (idx+1) % 1000 == 0:
            print idx+1
            
    data_file.close()
    desc_file.close()
    id_map.close()
