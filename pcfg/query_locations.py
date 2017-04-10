import pickle
import sys

def query_locations(city, ngh):
	try:
		picklefile = open("ngh_locations/ngh_data/pickle/" + str(city).lower() + ".pickle", "r")
		dic = pickle.load(picklefile)
		return dic[ngh.lower()]
	except:
		return []

if __name__ == '__main__':
	c = sys.argv[1]
	n = sys.argv[2]
	query_locations(c, n)