import pickle
import sys

# lat: latitude
# lng: longitude
# att: list of attractions
# max_walk: maximum acceptable walking time in minutes
def distance_attractions(lat, lng, att, max_walk):
	try:
		pass
	# 	picklefile = open("ngh_locations/ngh_data/pickle/" + str(city).lower() + ".pickle", "r")
	# 	dic = pickle.load(picklefile)
	# 	return dic[ngh.lower()]
		return 'A short walk'
	except:
		return 'unknown'

if __name__ == '__main__':
	att = ['roslindale village', 'roslindale square', 'the arnold arboretum', 'emerald necklace']
	att = ['jp, the arnold arboretum, jamaica, jamaica pond']
	att = ['the museum of fine arts', 'longwood', 'northeastern university', 'penguin pizza']
	print distance_attractions(att=att, max_walk=60)
