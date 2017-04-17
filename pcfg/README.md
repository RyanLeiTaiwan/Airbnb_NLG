## Custom PCFG script
Usage:
<pre>custom_pcfg.py grammar_file csv_file #skip_rows #generate_rows [output_pcfg output_random]</pre>
- **#skip_rows**: the number of first rows to skip (in addition to header). **#skip_rows = 0** if you want to start from the first property.
- **#generate_rows**: the number of rows to generate output.
- (Optional) **output_pcfg**: the output file for normal PCFG with mined information.
- (Optional) **output_random**: the output file for random choices of mined information.

Standard output will always print the normal PCFG version with an additional newline after one property.

File output will be exactly one line per property.
