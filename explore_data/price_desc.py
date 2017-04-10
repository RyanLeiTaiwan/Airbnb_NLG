import csv
from collections import defaultdict

def adj_price(accom, price):
	try:
        	guests = float(accom)
                price_str = price.replace("$","").replace(",","")
                price = float(price_str)
                price_per = price/guests

		if price_per < 34:
			return "cheap"
		elif price_per < 116:
			return "affordable"
		else:
			return "luxurious"
        except:
                return "affordable"


def test():
	reader = csv.reader(open("data.csv", "rb"))
	for line in reader:
		print adj_price(line[16], line[23])

def overview():
	reader = csv.reader(open("data.csv", "rb"))
	price_list = []

	for line in reader:
		try:
			guests = float(line[16])
			price_str = line[23].replace("$","").replace(",","")
			price = float(price_str)
			price_list.append(price/guests)
		except:
			print line[16], line[23]
			continue

	price_list = list(set(price_list))
	price_list.sort()

	tot_prices = len(price_list)
	
	print price_list[tot_prices/3]
	print price_list[tot_prices/2]
	print price_list[4*tot_prices/5]

	#print price_list

#overview()
test()
			
