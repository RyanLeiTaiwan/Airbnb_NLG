import os
import sys
import csv
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk import pos_tag

import pickle

fields = {}
ngh_adjs = {}

with open(sys.argv[1], "rb") as csvfile:
	city = csv.reader(csvfile, delimiter=',', quotechar='"')		
	counter = 0
	count2 = 0
	for row in city:
		if counter == 0:
			inner_counter = 0
			for f in row:
				fields[f.strip()] = inner_counter
				inner_counter += 1
		else:
			try:
				if len(row[fields['neighbourhood_cleansed']]) > 1:
						n = row[fields['neighbourhood_cleansed']].strip().lower()
						d = row[fields['description']]
						s = sent_tokenize(d)
						for t in s:
							search = '%s is' % (n)
							n_idx = t.lower().find(search)
							if n_idx > -1:
								tags = pos_tag(word_tokenize(t[n_idx:]))
								for tag in tags:
									if tag[1] == 'JJ':
										if n in ngh_adjs:
											ngh_adjs[n].append(tag[0])
										else:
											ngh_adjs[n] = [tag[0]]
			except:
				pass
		counter += 1

picklefile = open(sys.argv[2], "w")
pickle.dump(ngh_adjs, picklefile)
picklefile.close()