import csv
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from collections import defaultdict


csvFile = "/home/extrared/Documents/Airbnb/src/Boston_details.csv"

def adj_size(accom, ba, br, beds):
	try:
		if float(accom) >= 3 and float(ba) >= 1 and float(br) >= 2 and float(beds) >= 2:
			return "spacious"
	except ValueError:
		return "cozy"
	
	return "cozy"

def adj_size_ml(accom, ba, br, beds): 
	weights = [ 0.05563686, -0.04954873, 0.06664001, -0.0241994, -0.12234109 ]
	features = [accom, ba, br, beds, "1"]
	logit = 0.0
	for i in range(0, len(weights)):
		if len(features[i]) == 0:
			continue
		logit += float(features[i])*weights[i]
	if 1.0/(1.0+np.exp(logit)) < 0.5:
		return "spacious"
	else:
		return "cozy"

def overview(df_size_info):
	cnt = 0
	accom = defaultdict(float)
	ba = defaultdict(float)
	br = defaultdict(float)
	bed = defaultdict(float)

	sp_accom = defaultdict(float)
	sp_ba = defaultdict(float)
	sp_br = defaultdict(float)
	sp_bed = defaultdict(float)


	tot_spacious = 0
	pred_spacious = 0
	matched = 0
	print "property_type, room_type, accommodates, beds, bedrooms, bathrooms"
	for index, row in df_size_info.iterrows():	
		cnt += 1
		accomodates = row['accommodates']
		bathroom = row['bathrooms']
		bedroom = row['bedrooms']
		beds = row['beds']
	
		accom[accomodates] += 1
		ba[bathroom] += 1
		br[bedroom] += 1
		bed[beds] += 1

		if row['description'].find("spacious") != -1:
			tot_spacious += 1
			sp_accom[accomodates] += 1
			sp_ba[bathroom] += 1
			sp_br[bedroom] += 1
			sp_bed[beds] += 1	

		if float(accomodates) >= 3 and float(bathroom) >= 1 and float(bedroom) >= 2:
			pred_spacious += 1
			if row['description'].find("spacious") != -1:
				matched += 1
	print "accomo", sp_accom, accom
	print "bathrooms", sp_ba, ba
	print "bedrooms", sp_br, br
	print "beds", sp_bed, bed
	print tot_spacious, pred_spacious, matched

def gen_features(feature_set, df_size_info):
	first_flag = True
	X = []
	y = []
	for index, row in df_size_info.iterrows():
		if first_flag:
			first_flag = False
			continue
		one_feature = []
		for f in feature_set:
			one_feature.append(float(row[f]))
		X.append(one_feature)
		if row['description'].find("spacious") != -1:
			y.append(1)
		else:
			y.append(0)
	return X, y

def train(df_size_info):
	indices = ["accommodates", "bathrooms", "beds", "bedrooms"]
	X, y = gen_features(indices, df_size_info)
	print np.sum(y)
	#clf = SVC(gamma=3, C=1)
	clf = LogisticRegression(C=0.001, penalty='l2', tol=0.001, class_weight="auto")
	clf.fit(X, y)
	print np.sum(clf.predict(X))
	print "matched", np.sum(clf.predict(X) & y)

	coef = clf.coef_.ravel()
	print clf.intercept_
	print "coef", coef
	print "score", clf.score(X, y)

def test():
	first_flag = True
	for line in reader:
		if first_flag:
			first_flag = False
			continue	
		print adj_size_ml(line[16], line[17], line[18], line[19])

if __name__ == '__main__':
	df = pd.read_csv(csvFile)
	df_size_info = df.loc[:, ['description', 'property_type', 'room_type', 'accommodates', 'beds', 'bedrooms', 'bathrooms']]
	df_size_info = df_size_info.fillna(0.0)
	#train(df_size_info)
	# test()
	overview(df_size_info)
