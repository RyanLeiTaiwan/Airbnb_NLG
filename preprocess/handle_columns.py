"""
Handlers of specific CSV columns
"""
import re


def handle_amenities(amens):
    amens_rgx = re.compile('[^0-9a-zA-Z ]+')
    amens = (amens.replace(",", " ")).lower()
    amens = re.sub(amens_rgx, "", amens)
    return amens
