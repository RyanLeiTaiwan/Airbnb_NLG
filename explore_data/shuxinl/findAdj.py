from __future__ import unicode_literals
import spacy
import sys
import os
import operator
from collections import Counter, defaultdict

def get_character_adjectives(doc, character_lemma):
    """
    Find all the adjectives related to `character_lemma` in `doc`
    
    :param doc: Spacy NLP parsed document
    :param character_lemma: string object
    :return: list of adjectives related to `character_lemma`
    """
    
    adjectives = []
    for ent in doc.ents:
        if ent.lemma_ == character_lemma:
            for token in ent.subtree:
                if token.pos_ == 'ADJ': # Replace with if token.dep_ == 'amod':
                    adjectives.append(token.lemma_)
    
    for ent in doc.ents:
        if ent.lemma_ == character_lemma:
            if ent.root.dep_ == 'nsubj':
                for child in ent.root.head.children:
                    if child.dep_ == 'acomp':
                        adjectives.append(child.lemma_)
    
    return adjectives

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
print(get_character_adjectives(doc, 'cambridge'))
