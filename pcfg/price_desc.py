import csv
import pandas as pd
from collections import defaultdict

csvFile = "/home/extrared/Documents/Airbnb/src/Boston_details.csv"

def adj_price(accom, price):
	try:
        	guests = float(accom)
                price_str = price.replace("$","").replace(",","")
                price = float(price_str)
                price_per = price/guests

		if price_per < 39:
			return "cheap"
		elif price_per < 98:
			return "affordable"
		else:
			return "luxurious"
        except:
                return "affordable"


def test():
	for line in reader:
		print adj_price(line[16], line[23])

def overview(df_price_info):
	price_list = []

	for index, row in df_price_info.iterrows():
		guests = float(row['accommodates'])
		price_list.append(row['price']/guests)

	price_list = list(set(price_list))
	price_list.sort()

	tot_prices = len(price_list)
	
	print price_list[tot_prices/3]
	print price_list[tot_prices/2]
	print price_list[4*tot_prices/5]

	#print price_list

if __name__ == '__main__':
	df = pd.read_csv(csvFile, converters={'price': lambda s: float(s.replace('$', '').replace(',', ''))})
	df_price_info = df.loc[:, ['description', 'accommodates', 'price']]
	df_price_info = df_price_info.fillna(0.0)

	overview(df_price_info)
	# test()
			
