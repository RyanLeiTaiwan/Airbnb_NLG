import csv
import nltk
import string
from nltk.corpus import stopwords

from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

csvFile = "/home/extrared/Documents/Airbnb/src/Boston_details.csv"
STOP = "STOP"

def basic_stat():
	srcf = open("transit.csv", "rb")
	reader = csv.reader(srcf)
	cnt = 0
	tot_len = 0
	for line in reader:
		tot_len += len(line[1])
		if len(line[1]) != 0:
			cnt += 1

	print cnt, tot_len/(float)(cnt) 
	
def get_neighbors():
	srcf = open("transit.csv", "rb")
	#srcf = open("src/Seattle_details.csv", "rb")
	reader = csv.reader(srcf)
	neighbor_dict = {}
	for line in reader:
		if line[2] in neighbor_dict:
			neighbor_dict[line[2]] += 1
		else:
			neighbor_dict[line[2]] = 1
	return neighbor_dict

def get_cnt(one_list):
    	all_cnt = {}
    	for item in one_list:
		if item in all_cnt:
       			all_cnt[item] += 1
		else:
            		all_cnt[item] = 1

	for item in all_cnt:
		all_cnt[item] = (float)(all_cnt[item])/len(one_list)
    	return all_cnt

def ngrams(neighborhood):
	srcf = open("transit.csv", "rb")
	reader = csv.reader(srcf)
 
	sw = set(stopwords.words('english'))
	
	unigrams = []
	for line in reader:
		if len(line[1]) == 0 or line[2] != neighborhood:
			continue
		text = line[1].lower().translate(None, string.punctuation)		
		terms = text.strip().split()
		for t in terms:
			if t not in sw:
				unigrams.append(t)
        	unigrams.append(STOP)

	bigram_tuples = list(nltk.bigrams(unigrams))
	trigram_tuples = list(nltk.trigrams(unigrams))	

	unigram_cnt = get_cnt(unigrams)
    	bigram_cnt = get_cnt(bigram_tuples)
    	trigram_cnt = get_cnt(trigram_tuples)

	top_unigram = sorted(unigram_cnt.items(), key=lambda x:x[1], reverse=True)
	top_bigram = sorted(bigram_cnt.items(), key=lambda x:x[1], reverse=True)
	top_trigram = sorted(trigram_cnt.items(), key=lambda x:x[1], reverse=True)

	print "***************"+neighborhood+"*****************"
	print top_unigram[:30]
	print top_bigram[:30]
	print top_trigram[:30]

	srcf.close()

def neigh_vs_vech(df_transit):
	common_transits = ['bus', 'rail', 'uber/lyft', 'taxi', 'bike/bicycle']
	all_nhoods = df.groupby('neighbourhood_cleansed').size().to_dict()
	print all_nhoods
	neigh_trans_dict = defaultdict(Counter)

	for index, row in df_transit.iterrows():
		transit_text = str(row['transit'])
		neighbor = str(row['neighbourhood_cleansed'])

		if len(transit_text) == 0:
			continue
		text = transit_text.lower().translate(None, string.punctuation)		
		terms = set(text.lower().strip().split())
		for t in terms:
			if t in common_transits:
				neigh_trans_dict[t][neighbor] += 1    
			if t == 'uber' or t == 'lyft':
				neigh_trans_dict['uber/lyft'][neighbor] += 1
			if t == 'bike' or t == 'bicycle':
				neigh_trans_dict['bike/bicycle'][neighbor] += 1

	for trans in common_transits:
		for nei in all_nhoods:
			neigh_trans_dict[trans][nei] = neigh_trans_dict[trans][nei]/(float)(all_nhoods[nei])

	neigh_trans_df = pd.DataFrame.from_dict(dict(neigh_trans_dict), dtype=float)
	neigh_trans_full_df = neigh_trans_df.fillna(value=0).astype(float)

	plt.figure()
	hmap = sns.heatmap(neigh_trans_full_df, annot=True, fmt='f', cmap='YlGnBu', cbar=False)
	plt.title('Popular transportation tools metioned')
	plt.yticks(rotation=30)
	plt.show()

def neigh_vs_loc():
	common_locations = ['airport', 'downtown', 'mall/market', 'university', 'hill']

	srcf = open("transit.csv", "rb")
	reader = csv.reader(srcf)
 
	neigh_loc_dict = defaultdict(Counter)
	for line in reader:
		if len(line[1]) == 0:
			continue
		text = line[1].lower().translate(None, string.punctuation)		
		terms = set(text.lower().strip().split())
		for t in terms:
			if t in common_locations:
				neigh_loc_dict[t][line[2]] += 1    
			if t == 'mall' or t == 'market':
				neigh_loc_dict['mall/market'][line[2]] += 1

	for trans in common_locations:
		for nei in nhoods.keys():
			neigh_loc_dict[trans][nei] = neigh_loc_dict[trans][nei]/(float)(nhoods[nei])

	srcf.close()
	
	neigh_loc_df = pd.DataFrame.from_dict(dict(neigh_loc_dict), dtype=float)
	neigh_loc_full_df = neigh_loc_df.fillna(value=0).astype(float)

	plt.figure()
	hmap = sns.heatmap(neigh_loc_full_df, annot=True, fmt='f', cmap='YlGnBu', cbar=False)
	plt.title('Popular location name entities metioned')
	plt.yticks(rotation=30)
	plt.show()

def walkscore(neighborhood):
	reader = csv.reader(open("walkscore.csv", "rb"))
	scores = {}
	cur_scores = []
	descrips = ["Very convenient to walk to nearby facilities and attractions, daily errands do not require a car",
	            "Transit is convenient for most trips, easy to get access to buses and rails",
	            "The neighborhood is flat as a pancake, and has excellent bike lanes"]
	# Ryan: Return a single description with the best rank, or "" if worse than threshold
	ranks = [0,0,0]

	for line in reader:
		scores[line[0].lower()] = (line[1], line[2], line[3])
		if line[0].lower() == neighborhood.lower():
			cur_scores.append(line[1])
			cur_scores.append(line[2])
			cur_scores.append(line[3])

	tot_neighs = len(scores)
	for i in range(0, 3):
		rank = 0
		for s in scores:
			if scores[s][i] > cur_scores[i]:
				rank += 1
				ranks[i] += 1
		if rank > tot_neighs/3:
			descrips[i] = ""
	
	# print descrips
	# The best-ranked description can be an empty string
	return descrips[np.argmin(ranks)]
	

if __name__ == '__main__':
	df = pd.read_csv(csvFile, dtype={'neighbourhood_cleansed':np.str_, 'transit':np.str_})
	df_transit = df.loc[:, ['neighbourhood_cleansed', 'transit']]
	
	#basic_stat()
	#nhoods = get_neighbors()
	#for neighbor in nhoods:
	#	ngrams(neighbor)

	#neigh_vs_vech(df_transit)
	#neigh_vs_loc()
