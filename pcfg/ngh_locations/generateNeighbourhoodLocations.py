from __future__ import unicode_literals
import spacy
import sys
import os
import operator
from collections import Counter, defaultdict
import pickle

#PERSON	People, including fictional.
#NORP	Nationalities or religious or political groups.
#FACILITY	Buildings, airports, highways, bridges, etc.
#ORG	Companies, agencies, institutions, etc.
#GPE	Countries, cities, states.
#LOC	Non-GPE locations, mountain ranges, bodies of water.
#PRODUCT	Objects, vehicles, foods, etc. (Not services.)
#EVENT	Named hurricanes, battles, wars, sports events, etc.
#WORK_OF_ART	Titles of books, songs, etc.
#LANGUAGE	Any named language.
#DATE	Absolute or relative dates or periods.
#TIME	Times smaller than a day.
#PERCENT	Percentage, including "%".
#MONEY	Monetary values, including unit.
#QUANTITY	Measurements, as of weight or distance.
#ORDINAL	"first", "second", etc.
#CARDINAL	Numerals that do not fall under another type.
def find_character_occurences(doc):
    """
    Return a list of actors from `doc` with corresponding occurences.
    
    :param doc: Spacy NLP parsed document
    :return: list of tuples in form
        [('elizabeth', 622), ('darcy', 312), ('jane', 286), ('bennet', 266)]
    """
    
    characters = Counter()
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'GPE', 'LOC', 'FAC']:
            characters[ent.lemma_] += 1
            
    return characters.most_common()

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('utf8')

	#spacy.util.set_data_path("/Users/susie/git/") 
	nlp = spacy.load('en')
	city = sys.argv[1]
	description = "./ngh_data/" + city + "/"

	dic = {}

	for file in os.listdir(description):
		with open(str("./ngh_data/" + str(city) + "/" + str(file)), 'r') as myfile:
		    text = myfile.read()

		doc = nlp(text.decode('utf-8'))
		ngh = file[:-4].replace("_", " ").lower()
		dic[ngh] = []
		locs = find_character_occurences(doc)
		for x in locs:
			if (x[1] > 2) and x[0] != city.lower():
				if x[0] != "" and x[0] != ngh:
					dic[ngh].append(x[0])
	picklefile = str(city).lower() + ".pickle"
	p_file = open(picklefile, "w")
	pickle.dump(dic, p_file)
	p_file.close()