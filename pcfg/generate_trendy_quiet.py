import sys
import os
import pickle
import matplotlib
import csv
from stop_words import get_stop_words
import string
import operator
import copy
import numpy as np

def get_features(filename):
	
	stops = get_stop_words('en')

	fields = {}

	trendy_count = 0
	untrendy_count = 0

	word_dict = {}

	csvfile = open(filename, "rb")
	city = csv.reader(csvfile, delimiter=',', quotechar='"')
	for count, row in enumerate(city):
		if count == 0:
			for idx in range(0, len(row)):
				fields[row[idx]] = idx
		else:
			ngh_idx = fields['neighbourhood_cleansed']
			dsc_idx = fields['description']

			ngh = row[ngh_idx]

			trendy_idx = row[dsc_idx].lower().find("trendy")
			calm_idx = row[dsc_idx].lower().find("calm")
			peace_idx = row[dsc_idx].lower().find("peaceful")
			
			if trendy_idx > -1:
				trendy_count += 1
				words = row[dsc_idx].lower().translate(None, string.punctuation).split()
				for word in words:
					if word not in stops:
						if word in word_dict:
							word_dict[word] += 1
						else:
							word_dict[word] = 1
			elif calm_idx > -1 or peace_idx > -1:
				untrendy_count += 1
				words = row[dsc_idx].lower().translate(None, string.punctuation).split()
				for word in words:
					if word not in stops:
						if word in word_dict:
							word_dict[word] += 1
						else:
							word_dict[word] = 1

	csvfile.close()

	top_terms = sorted(word_dict.items(), key=operator.itemgetter(1), reverse = True)[:500]
	cnt = 0
	features = {}
	for x in top_terms:
		features[x[0]] = cnt
		cnt += 1
	return features

def build_features(filename, features):

	fields = {}

	word_dict = {}

	feat_vecs = []

	csvfile = open(filename, "rb")
	city = csv.reader(csvfile, delimiter=',', quotechar='"')
	for count, row in enumerate(city):
		if count == 0:
			for idx in range(0, len(row)):
				fields[row[idx]] = idx
		else:
			ngh_idx = fields['neighbourhood_cleansed']
			dsc_idx = fields['description']

			ngh = row[ngh_idx]

			trendy_idx = row[dsc_idx].lower().find("trendy")
			calm_idx = row[dsc_idx].lower().find("calm")
			peace_idx = row[dsc_idx].lower().find("peaceful")
			
			vec = [0] * len(feats)

			if trendy_idx > -1:
				words = row[dsc_idx].lower().translate(None, string.punctuation).split()
				for word in words:
					if word in feats:
						vec[feats[word]] += 1
				feat_vecs.append((copy.deepcopy(np.array(vec)), True))
			elif calm_idx > -1 or peace_idx > -1:
				words = row[dsc_idx].lower().translate(None, string.punctuation).split()
				for word in words:
					if word in feats:
						vec[feats[word]] += 1
				feat_vecs.append((copy.deepcopy(np.array(vec)), False))


	csvfile.close()

	return feat_vecs

def train(filename, feats, vectors):

	fields = {}

	ngh_stats = {}

	csvfile = open(filename, "rb")
	city = csv.reader(csvfile, delimiter=',', quotechar='"')
	for count, row in enumerate(city):
		if count == 0:
			for idx in range(0, len(row)):
				fields[row[idx]] = idx
		else:
			ngh_idx = fields['neighbourhood_cleansed']
			dsc_idx = fields['description']


			ngh = row[ngh_idx]

			if ngh not in ngh_stats:
				ngh_stats[ngh] = [0,0]
			
			vec = [0] * len(feats)

			words = row[dsc_idx].lower().translate(None, string.punctuation).split()
			for word in words:
				if word in feats:
					vec[feats[word]] += 1
			
			array = np.array(vec)


			min_dist = None
			min_label = None

			for v in vectors:
				d = np.linalg.norm(vec-v[0])
				if min_dist is None or min_dist > d:
					min_dist = d
					min_label = v[1]

			if min_label:
				ngh_stats[ngh][0] += 1
			else:
				ngh_stats[ngh][1] += 1

	csvfile.close()

	ngh_labels = {}

	for n in ngh_stats:
		if ngh_stats[n][0] > ngh_stats[n][1]:
			ngh_labels[n.lower()] = 'trendy'
		else:
			ngh_labels[n.lower()] = 'quiet'

	return ngh_labels



# input format:
# python generate_trendy_quiet.py /path/to/CSV city_name
if __name__ == "__main__":

	fields = {}
	nghs = {}

	count = 0

	feats = get_features(sys.argv[1])
	vectors = build_features(sys.argv[1], feats)
	labels = train(sys.argv[1], feats, vectors)

	city = sys.argv[2].lower()

	picklefile = open(city + "_trendy_quiet_labels.pickle", "w")
	pickle.dump(labels, picklefile)
	picklefile.close()
