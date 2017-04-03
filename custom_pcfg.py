import sys
import re
import copy
import random

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
			sys.stdout.write(self.text % tuple(values))
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
	"""Tree"""
	parse_data_file(sys.argv[2])
	root = build_tree(sys.argv[1])
	root.output()
	print ""


main()