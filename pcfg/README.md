## Randomly sample properties from CSV and output corresponding Airbnb human descriptions
Usage: 
<pre>sample.py input_csv num_samples output_csv output_human</pre>
Example (Sample 100 rows from Boston dataset): 
<pre>sample.py ../data/Boston_details.csv 100 sample/Boston_100.csv result/20170417/human_Boston_100.txt</pre>
- **num_samples**: number of rows (in addition to header) to sample
- **output_csv**: output file of the sampled CSV
- **output_human**: output file of the corresponding Airbnb human descriptions, one line per property

Set a fixed numpy random seed when we need reproducible results.
<pre>np.random.seed(11632)</pre>

Current implementation will only sample rows with non-NaN ['summary', 'accommodates', 'bathrooms', 'bedrooms', 'beds'], and output only the summary column in **output_human**.

## Custom PCFG script
Usage:
<pre>custom_pcfg.py grammar_file csv_file #skip_rows #generate_rows [output_pcfg output_random]</pre>
Example (Run all 100 rows):
<pre>custom_pcfg.py grammar/updated_airbnb_grammar.txt sample/Boston_100.csv 0 100 result/20170417/pcfg_Boston_100.txt result/20170417/random_Boston_100.txt</pre>
Example (Skip the first 1000 rows and run only rows 1001 to 1003, but don't output to files):
<pre>custom_pcfg.py grammar/updated_airbnb_grammar.txt ../data/Boston_details.csv 1000 3</pre>
- **#skip_rows**: number of first rows to skip (in addition to header). **#skip_rows = 0** if you want to start from the first property.
- **#generate_rows**: number of rows to generate output.
- (Optional) **output_pcfg**: output file of normal PCFG with mined information, one line per property.
- (Optional) **output_random**: output file of PCFG with random choices for mined information, one line per property.

Set a fixed Python random seed when we need reproducible results
<pre>random.seed(11632)</pre>

Standard output will always print the normal PCFG version with an additional newline after each property.

Current implementation ensures the normal and random PCFG will choose the same grammar rules. Only the values of mined information are different.

## Template-based method
Usage:
<pre>templated.py csv #skip_rows #generate_rows</pre>
Example (Run all 100 rows):
<pre>templated.py sample/Boston_100.csv 0 100 > result/20170417/template_Boston_100.txt</pre>
- **#skip_rows**: number of first rows to skip (in addition to header). **#skip_rows = 0** if you want to start from the first property.
- **#generate_rows**: number of rows to generate output.

Result is shown in standard output.

