# All functions related to formatting the text for easy Google Form copy and paste
from preprocess.handle_columns import *
import re

# Format columns for one CSV row as multiple lines for human investigation or human rating survey
# Rename column names as appropriate
"""
Format:
- col0: value0
- col1: value1
...
"""
def format_csv_row(survey_cols, row):
    data_str = []
    for col in survey_cols:
        value = row[col]
        value = re.sub('\s+', ' ', value).strip()
        if col == 'id':
            # Airbnb listing URL
            col = 'listing'
            info = 'https://www.airbnb.com/rooms/' + value
        elif col == 'name':
            col = 'title'
            info = value
        elif col == 'street':
            info = handle_street(value)
        elif col == 'neighbourhood_cleansed':
            col = 'neighbourhood'
            info = value
        else:
            info = value
        data_str.append('- ' + col + ': ' + info)
    return '\n'.join(data_str)


# TODO: Tweak Google Form multi-line NLG string format and return a new string
# - Capitalize sentence starts
# - Remove spaces before punctuations
# Example NLG string:
"""
the living space place is located in a quiet neighborhood in the heart of the city of copenhagen. enjoy 4 rooms

free wifi , tv , kitchen , washing machine , microwave , oven , microwave , dishwasher , microwave , oven , fridge , microwave , oven , toaster , water boiler , a toaster , electric kettle , toaster .

our property is located close to ucsd , shopping mall , supermarket , restuarants and all kind of shops . located just off the freeway , just 10 minutes away from downtown san diego , 4 miles from beach gym transport service . less than a mile from the 163 and 57 freeways so you can enjoy the wide variety of restaurants , shops and groceries . walking distance to the i-5 , shopping malls and a few more there are several art galleries .

short walking distance to the diego zoo , 15 miles to old town , 15 min to pacific beach , 15 minutes to coronado 's zoo and less than 10 min to downtown valley and 30 min from sd jolla . coliseum , hillcrest , pacific cliffs , gaslamp area , hillcrest , children 's hospital , mission cross , coronado , playa del balboa , etc .

there are two major rail lines ( arcadia and san diego blvd bus stations nearby straight in 20 minutes ) , the is located in a great neighborhood nestled at a backyard . cable car , public car rtd bus nearby , including bus lines , trolley stations , restaurants , coffee shops , easy parking , safe and roomy friendly family .
"""
def format_nlg(s):
    s = s[0].upper() + s[1:]
    s = re.sub(r'\( +', '(', s)
    s = re.sub(r' +\)', ')', s)
    s = re.sub(r' +,', ',', s)
    s = re.sub(r' +\.', '.', s)
    s = re.sub(r' +\?', '?', s)
    s = re.sub(r' +\!', '!', s)
    p = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    s = p.sub(lambda x: x.group().capitalize(), s)
    return s
