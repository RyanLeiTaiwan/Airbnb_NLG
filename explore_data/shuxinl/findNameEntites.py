from __future__ import unicode_literals
import spacy
import sys
import os
import operator
from collections import Counter, defaultdict

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

	spacy.util.set_data_path("/Users/susie/git/") 
	nlp = spacy.load('en')
	city = sys.argv[1]
	neighbourhood = sys.argv[2]
	description = "./data/imtermidiate_data/" + city + "/" + neighbourhood + '.txt'

	with open(description, 'r') as myfile:
	    text = myfile.read()

	doc = nlp(text.decode('utf-8'))

	print(find_character_occurences(doc)[:10])
