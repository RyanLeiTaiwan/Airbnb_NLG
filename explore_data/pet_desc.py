import csv
import pandas as pd


def adj_pets(amenity):
	if amenity.lower().find("pets allowed") != -1:
		return "Pets are allowed."
	else:
		return "No pet is allowed."

def overview():
	reader = csv.reader(open("data.csv", "rb"))
	for line in reader:
		amenity = line[21].lower()
		if amenity.find("pets allowed") != -1:
			print amenity

overview()
