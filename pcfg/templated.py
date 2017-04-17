import sys
import pandas as pd
import numpy as np

def dollar_filter(s):
    return float(s.replace('$', '').replace(',', ''))

if __name__ == '__main__':
	# Set random seed so the result is reproducible
	np.random.seed(11632)
	pd.set_option('display.width', 150)
	pd.set_option('max_colwidth', 80)
	pd.set_option('max_rows', 500)

	# Check usage
	if len(sys.argv) != 4:
		print 'Usage: %s csv #skip_rows #generate_rows' % sys.argv[0]
		exit(0)

	csv_file = sys.argv[1]
	skip_rows = int(sys.argv[2])
	generate_rows = int(sys.argv[3])

	# Avoid using np.float for "1 bedroom" kind of sentences
	dtype_dict = {
		'id': np.str, 'accommodates': 'category', 'bathrooms': 'category', 'bedrooms': 'category',
		'beds': 'category', 'neighbourhood_cleansed': 'category'
	}
	converter_dict = {'price': dollar_filter}
	df = pd.read_csv(csv_file, skiprows=skip_rows, nrows=generate_rows, dtype=dtype_dict, converters=converter_dict)

	for index, row in df.iterrows():
		# Modified template from Trulia's version
		"""
		We have a [bedrooms]-bedroom, [bathrooms]-bathroom [property_type] on [street] in the
		[neighbourhood_cleansed] neighborhood in [city].
		This [property_type] has [beds] beds and can accommodate [accommodates] people.
		The price per night is $[price], or ${[price]/[accommodates]} per person. 
		"""
		output_str = ''
		output_str += 'We have a %s-bedroom, %s-bathroom %s on %s in the %s neighborhood in %s. '
		output_str += 'This %s has %s beds and can accommodate %s people. '
		output_str += 'The price per night is $%.2f, or $%.2f per person.'
		values = (
			row.bedrooms, row.bathrooms, row.property_type, row.street.split(',')[0],
			row.neighbourhood_cleansed, row.city, row.property_type, row.beds, row.accommodates,
			float(row.price), float(row.price) / float(row.accommodates)
		)
		print output_str % values
