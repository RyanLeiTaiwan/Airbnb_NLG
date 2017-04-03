import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

reader = csv.reader(open("data.csv", "rb"))

def overview():
	cnt = 0
	accom = 0.0
	ba = 0.0
	br = 0.0
	bed = 0.0
	guest = 0.0

	empty = 0

	print "property_type, room_type, accom, ba, br, beds, bed_type, guests"
	for line in reader:
		cnt += 1
		try:
			accom += float(line[17])
			ba += float(line[18])
			br += float(line[19])
			bed += float(line[20])
			guest += float(line[-1])
		except ValueError:
			pass

		if line[2].find("spacious") != -1:
			print line[15:22], line[-1]
	print accom/cnt, ba/cnt, br/cnt, bed/cnt, guest/cnt

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
	indices = [17, 18, 19, 20, 24]
	X, y = gen_features(indices)
	#clf = SVC(gamma=3, C=1)
	clf = LogisticRegression(C=0.1, penalty='l2', tol=0.001, class_weight="auto")
	clf.fit(X, y)
	print np.sum(clf.predict(X))
	#coef_LR = clf_LR.coef_.ravel()
	#print "coef", coef_LR
	print "score", clf.score(X, y)
	
	
train()	
