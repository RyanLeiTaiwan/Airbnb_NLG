import pickle
import sys
import random

def query_ngh_adjs(city, ngh):
	try:
		picklefile = open("neighbourhood_adjectives/pickles/" + str(city).lower() + ".pickle", "r")
		dic = pickle.load(picklefile)
		return random.choice(dic[ngh.lower()]).lower()
	except:
		return None

if __name__ == '__main__':
	c = sys.argv[1]
	n = sys.argv[2]
	print query_ngh_adjs(c, n)