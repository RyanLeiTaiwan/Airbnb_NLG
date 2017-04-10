import sys
import re
import copy
import random
import csv
import query_locations as qry_locs
import google_api

from size_desc import adj_size
from pet_desc import adj_pets
from price_desc import adj_price

global_nodes = {}
nodes = {}

data_dict = {}

def parse_data_file(data_file):
	global data_dict

	df = open(data_file, "r")

	for line in df:
		line = line.strip()
		key, value = line.split(",")
		data_dict[key.strip()] = value.strip()

def build_dict(bdrm, bath, sqft, street, ngh, city, property_type,
               lat, lng):
	global data_dict

	data_dict = {}

	# Factual information
	data_dict["bedroom"] = bdrm
	data_dict["bathroom"] = bath
	data_dict["square_feet"] = sqft
	data_dict["neighbourhood_cleansed"] = ngh
	data_dict["city"] = city
	data_dict["street_name"] = street.split(",")[0]
	data_dict["property_type"] = property_type

	# Mined information
	# Top 4 neighborhood attractions
	ngh_attractions = qry_locs.query_locations(city, ngh)[:4]
	data_dict["neighbourhood_attractions"] = ", ".join(ngh_attractions)
	data_dict["distance_attraction"] = google_api.distance_attractions(
		lat=lat, lng=lng, att=ngh_attractions, max_walk=60)
	# data_dict["distance_attraction"] = "A short walk"

	# Temporary default values for things we cant generate yet...
	data_dict["a:square_feet"] = adj_size(row[53], row[54], row[55], row[56])
	data_dict["transportation"] = "The L train"
	data_dict["distance_transport"] = "A short walk"
	data_dict["a:property"] = "Modern"
	data_dict["transport_hub"] = "Grand Central Station"
	data_dict["attraction_type"] = "locations"
	data_dict["a:price"] = adj_price(row[53], row[60])
	data_dict["a:neighbourhood"] = "Young"

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

	def output(self):
		if self.is_leaf:
			values = []
			for key in self.fillers:
				if key in data_dict:
					values.append(data_dict[key])
				else:
					values.append("[" + key + "]")
			sys.stdout.write(self.text % tuple(values) + " ")
		else:	
			c = random.choice(self.children)
			for child in c:
				global_nodes[child].output()

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
	if len(sys.argv) != 5:
		print 'Usage: %s grammar csv #skip_rows #generate_rows' % sys.argv[0]
		exit(0)

	root = build_tree(sys.argv[1])
	skip_rows = int(sys.argv[3])
	generate_rows = int(sys.argv[4])
	total_rows = skip_rows + generate_rows

	with open(sys.argv[2], "rb") as csvfile:
		city = csv.reader(csvfile, delimiter=',', quotechar='"')
		for counter, row in enumerate(city):
			# Skip the first #skip_rows rows and header row
			if counter <= skip_rows:
				continue
			elif counter > total_rows:
				break

			# bdrm, bath, sqft, street, ngh, city, property_type
			# lat, lng
			build_dict(row[55], row[54], row[59], row[37], row[39], row[41], row[51],
			           row[48], row[49])
			root.output()
			print "\n"

main()