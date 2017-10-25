"""
Handlers of specific CSV columns
"""
import re


def handle_amenities(amens):
    amens_rgx = re.compile('[^0-9a-zA-Z ]+')
    amens = (amens.replace('\n', '').replace(',', ' ')).lower()
    amens = re.sub(amens_rgx, '', amens)
    return amens

def handle_street(st):
    return st.split(',')[0]


def handle_bedrooms_bathrooms(brba, col_names):
    return brba + ' ' + col_names