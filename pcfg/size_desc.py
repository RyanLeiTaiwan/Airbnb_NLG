import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from collections import defaultdict

# Comment this function so this file can be imported
# reader = csv.reader(open("data.csv", "rb"))


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

def overview():
	cnt = 0
	accom = defaultdict(float)
	ba = defaultdict(float)
	br = defaultdict(float)
	bed = defaultdict(float)
	guest = defaultdict(float)

	spacious = 0
	matched = 0

	print "property_type, room_type, accom, ba, br, beds, bed_type, guests"
	for line in reader:
		cnt += 1
		try:
			accom[float(line[16])] += 1
			ba[float(line[17])] += 1
			br[float(line[18])] += 1
			bed[float(line[19])] += 1
			guest[float(line[-1])] += 1
			
			if float(line[16]) >= 3 and float(line[17]) >= 1 and float(line[18]) >= 2 and float(line[19]) >= 2:
				spacious += 1
				if line[2].find("spacious") != -1:
					matched += 1
		except ValueError:
			pass

		#if line[2].find("spacious") != -1:
		#	print line[15:22], line[-1]
	print accom
	print ba
	print br
	print bed
	print guest
	print spacious, matched

def gen_features(indices):
	first_flag = True
	X = []
	y = []
	for line in reader:
		if first_flag:
			first_flag = False
			continue
		one_feature = []
		for i in indices:
			if len(line[i]) != 0:
				one_feature.append(float(line[i]))
			else:
				one_feature.append(0.0)
		X.append(one_feature)
		if line[2].find("spacious") != -1:
			y.append(1)
		else:
			y.append(0)
	return X, y

def train():
	indices = [16, 17, 18, 19]
	X, y = gen_features(indices)
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
	# train()
	# test()
	overview()
