# -*- coding: UTF-8 -*-
import sys
import re
import copy
import random
import csv
import pickle
import query_locations as qry_locs
from operator import itemgetter
import query_trendy as qry_trendy
import query_ngh_adjs as qry_ngh_adjs
import numpy as np

# Minxing
from size_desc import adj_size
from pet_desc import adj_pets
from price_desc import adj_price

# Ryan
import googlemaps # pip install googlemaps
import google_api
# Global Google API object
apikey = 'AIzaSyDpC11dt2AcHTva0XhKhwC3J0kvVJIGdkM'
api = googlemaps.Client(key=apikey)

global_nodes = {}
nodes = {}
data_dict = {}
data_dict_rand = {}

# Set a fixed random seed when we need reproducible results
random.seed(11632)


""" No longer used (prop.info)
def parse_data_file(data_file):
	global data_dict

	df = open(data_file, "r")

	for line in df:
		line = line.strip()
		key, value = line.split(",")
		data_dict[key.strip()] = value.strip()
"""

# Build all column information in a dictionary before running PCFG
# Data mining (enrichment) goes here
def build_dict(row):
	global data_dict, data_dict_rand, api

	data_dict = {}
	data_dict_rand = {}

	# Get specific column indices in CSV
	"""
	accommodates, bedrooms, bathrooms, square_feet, street, neighbourhood_cleansed, city,
	property_type, price, latitude, longitude
	"""
	(accm, bath, bdrm, beds, sqft, street, ngh, city,
	 property_type, price, lat, lng) \
		= itemgetter(53, 54, 55, 56, 59, 37, 39, 41,
		             51, 60, 48, 49)(row)

	# Factual information
	data_dict["bedroom"] = bdrm
	data_dict["bathroom"] = bath
	data_dict["square_feet"] = sqft
	data_dict["neighbourhood_cleansed"] = ngh
	data_dict["city"] = city
	data_dict["street_name"] = street.split(",")[0]
	data_dict["property_type"] = property_type

	### Temporary default values for things we cant generate yet...
	data_dict["transportation"] = "[The L train]"
	data_dict["distance_transport"] = "[A short walk]"
	data_dict["a:property"] = "[Modern]"
	data_dict["transport_hub"] = "[Grand Central Station]"
	data_dict["attraction_type"] = "[locations]"

	# Deep copy data_dict to data_dict_rand
	data_dict_rand = copy.deepcopy(data_dict)

	### Mined information
	# Adjectives for square feet and price
	data_dict["a:square_feet"] = adj_size(accm, bath, bdrm, beds)
	data_dict["a:price"] = adj_price(accm, price)
	# Top 3 neighborhood attractions
	ngh_attractions = qry_locs.query_locations(city, ngh)[:3]
	data_dict["neighbourhood_attractions"] = ", ".join(ngh_attractions)
	data_dict["distance_attraction"] = google_api.distance_attractions(
		api, lat, lng, city, ngh_attractions, max_walk=30)
	# Adjective (trendy or quiet) for neighborhood
	ngh_adj = qry_ngh_adjs.query_ngh_adjs(city, ngh)
	if ngh_adj is None:
		ngh_adj = qry_trendy.query_trendy(city, ngh)
	data_dict["a:neighbourhood"] = ngh_adj

	### Random versions of mined information
	data_dict_rand["a:square_feet"] = random.choice(['spacious', 'cozy'])
	data_dict_rand["a:price"] = random.choice(['cheap', 'affordable', 'luxurious'])

	# Instead of top 3 attractions in the correct neighborhood, choose 3 random city-level attractions
	city_attractions = []
	try:
		# Workaround to know the list of neighborhood in current city
		picklefile = open("ngh_locations/ngh_data/pickle/" + str(city).lower() + ".pickle", "r")
	except:
		# City name is wrong: do nothing
		pass
	else:
		dic = pickle.load(picklefile)
		# Build city-level attraction list each time (time-consuming)
		for attr in dic.values():
			city_attractions += attr
	ngh_attractions_rand = []
	length = len(city_attractions)
	if length > 3:
		ngh_attractions_rand = random.sample(city_attractions, 3)
	elif length > 0:
		ngh_attractions_rand = random.sample(city_attractions, length)

	data_dict_rand["neighbourhood_attractions"] = ", ".join(ngh_attractions_rand)
	data_dict_rand["distance_attraction"] = random.choice(['A short walk', 'A short drive'])
	data_dict_rand["a:neighbourhood"] = random.choice(['trendy', 'quiet'])

def parse_string(string):
	regex = re.compile("\[([^\]]*)\]")

	blanks = []

	for match in re.finditer(regex, string):
		s = match.group(0)
		blanks.append(s[1:len(s)-1])
	s = re.sub(regex, "%s", string)

	return (s, blanks)

class tree_node:
	"""A node in the tree"""

	#focus = []

	def __init__(self, l, s):
		global global_nodes

		self.label = l
		self.strings = copy.deepcopy(s)
		self.text = []
		self.is_leaf = False
		self.fillers = []
		self.children = []
		self.values = []
		for st in self.strings:
			if st[0] != '"':
				labels = st.split()
				self.children.append(copy.deepcopy(labels))
				for x in labels:
					if x not in global_nodes:
						global_nodes[x] = tree_node(x, nodes[x])
			else:
				# Leaf node
				tup = parse_string(st[1:len(st)-1])
				self.text = tup[0]
				self.fillers = copy.deepcopy(tup[1])
				self.set_leaf()

	def output(self, output_pcfg, output_random):
		if self.is_leaf:
			values = []
			values_rand = []
			for key in self.fillers:
				if key in data_dict:
					values.append(data_dict[key])
					values_rand.append(data_dict_rand[key])
				else:
					values.append("[" + key + "]")
					values_rand.append("[" + key + "]")
			# Print only the normal version on stdout
			sys.stdout.write(self.text % tuple(values) + " ")
			# Write both the normal and random versions to files
			try:
				if output_pcfg:
					output_pcfg.write(self.text % tuple(values) + " ")
			except UnicodeEncodeError:
				# TODO: Fix the unicode problem values
				# print 'self.text: ' + str(self.text)
				# print 'tuple(values): ' + str(tuple(values))
				pass
			try:
				if output_random:
					output_random.write(self.text % tuple(values_rand) + " ")
			except UnicodeEncodeError:
				# TODO: Fix the unicode problem values
				# print 'self.text: ' + str(self.text)
				# print 'tuple(values_rand): ' + str(tuple(values_rand))
				pass
		else:
			c = random.choice(self.children)
			for child in c:
				global_nodes[child].output(output_pcfg, output_random)

	def set_leaf(self):
		self.is_leaf = True


def build_tree(grammar_file):
	"""Build tree."""

	global nodes

	f = open(grammar_file, "r")

	for line in f:
		line = line.strip()
		if len(line) > 0:
			if line[0] != '#':
				label = None
				children = None
				try:
					label, children = line.split("->")
					label = label.strip()
					children = children.strip()
				except:
					print "ERROR on line:"
					print line
					print "No '->'"
					sys.exit()
				nodes[label] = []
				for x in children.split("|"):
					nodes[label].append(x.strip())

	f.close()

	n = None
	try:
		n = nodes['S']
	except:
		print "ERROR: NO 'S' NODE"
		sys.exit()

	root = tree_node('S', n)
	return root

def main():
	# Check command-line arguments
	argc = len(sys.argv)
	if argc != 5 and argc != 7:
		print 'Usage: %s grammar csv #skip_rows #generate_rows [output_pcfg output_random]' % sys.argv[0]
		exit(0)

	root = build_tree(sys.argv[1])
	skip_rows = int(sys.argv[3])
	generate_rows = int(sys.argv[4])
	total_rows = skip_rows + generate_rows

	output_pcfg = None
	output_random = None
	if argc == 7:
		output_pcfg = open(sys.argv[5], 'w')
		output_random = open(sys.argv[6], 'w')

	with open(sys.argv[2], "rb") as csvfile:
		city = csv.reader(csvfile, delimiter=',', quotechar='"')
		for counter, row in enumerate(city):
			# Skip the first #skip_rows rows and header row
			if counter <= skip_rows:
				continue
			elif counter > total_rows:
				break

			build_dict(row)
			root.output(output_pcfg, output_random)
			# Additional newlines
			print
			print
			if output_pcfg:
				output_pcfg.write('\n')
			if output_random:
				output_random.write('\n')

if __name__ == '__main__':
	main()