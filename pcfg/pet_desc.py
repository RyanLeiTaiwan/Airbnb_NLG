import csv
from collections import defaultdict

# Comment this function so this file can be imported
# reader = csv.reader(open("data.csv", "rb"))

def adj_pets(amenity):
	if amenity.lower().find("pets allowed") != -1:
		return "Pets are allowed."
	else:
		return "No pet is allowed."

def overview():
	for line in reader:
		amenity = line[21].lower()
		if amenity.find("pets allowed") != -1:
			print(amenity)

if __name__ == '__main__':
	overview()
