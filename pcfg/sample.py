import sys
import pandas as pd
import numpy as np

if __name__ == '__main__':
	# Set random seed so the result is reproducible
	np.random.seed(11632)
	pd.set_option('display.width', 150)
	pd.set_option('max_colwidth', 80)
	pd.set_option('max_rows', 500)

	# Check usage
	if len(sys.argv) != 5:
		print 'Usage: %s input_csv num_samples output_csv output_human' % sys.argv[0]
		exit(0)

	input_csv = sys.argv[1]
	num_samples = int(sys.argv[2])
	output_csv = sys.argv[3]
	# Output human summary as well
	output_human = sys.argv[4]

	dtype_dict = {'id': np.str, 'neighbourhood_cleansed': 'category'}
	df_all = pd.read_csv(input_csv, dtype=dtype_dict)
	# [Not needed] replace NaN values with '' in targeted textual columns
	# http://stackoverflow.com/questions/36556256/how-do-i-fill-na-values-in-multiple-columns-in-pandas
	# df_all.update(df_all['summary'].fillna(''))

	print df_all[['id', 'neighbourhood_cleansed']].describe()
	print
	print 'Original distribution:'
	print df_all.groupby('neighbourhood_cleansed').size().sort_values(ascending=False)

	# Randomly sample num_samples rows with non-nan summary, sorted by original index
	# Safely sample num_samples * 1.2 rows => drop summary NA => pick the first num_samples rows => sort by index
	df_sample = df_all.sample(n=int(num_samples * 1.2)).dropna(subset=['summary']).head(num_samples).sort_index()
	print
	print 'Sampled distribution:'
	print df_sample.groupby('neighbourhood_cleansed').size().sort_values(ascending=False)

	# Show the samples
	df_sample_print = df_sample[['id', 'neighbourhood_cleansed', 'summary']]
	print
	print '%d Samples:' % df_sample.shape[0]
	print df_sample_print

	# Write the sample into CSV file
	print
	print 'Writing sample to %s...' % output_csv
	df_sample.to_csv(output_csv, index=False)

	# Write the sample human summary to TXT file
	print
	print 'Writing human summary to %s...' % output_human
	fhuman = open(output_human, 'w')
	# print(df_sample.summary)
	summary = list(df_sample.summary)
	fhuman.writelines('\n'.join(summary))

