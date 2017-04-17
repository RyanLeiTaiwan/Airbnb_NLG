import pickle
import sys

def query_trendy(city, ngh):
	try:
		picklefile = open(str(city).lower() + "_trendy_quiet_labels.pickle", "r")
		dic = pickle.load(picklefile)
		return dic[ngh.lower()]
	except:
		return []

if __name__ == '__main__':
	c = sys.argv[1]
	n = sys.argv[2]
	print query_trendy(c, n)