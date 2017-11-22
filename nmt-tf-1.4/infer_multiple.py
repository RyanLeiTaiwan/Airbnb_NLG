import argparse
import os

def build_parser():
	parser = argparse.ArgumentParser(description='Generate descriptions.')
	parser.add_argument(
		'--model',
		required=True,
		help='trained model'
	)
	parser.add_argument(
		'--data',
		required=True,
		help='data input file'
	)
	parser.add_argument(
		'--output',
		required=True,
		help='output directory'
	)
	parser.add_argument(
		'--num_sent',
		default=10,
		help='number of descriptions for each property, default=10'
	)
	return parser
	
if __name__ == '__main__':
	parser = build_parser()
	args = parser.parse_args()
	src_files = []
	src_file_names = []
	#os.system("cd " + args.nmt)
	for i in range(int(args.num_sent)):
		cmd = "python -m nmt.nmt "
		cmd += "--inference_input_file=" + args.data + " "
		cmd += "--out_dir=" + args.model + " "

		temp_out = args.output + "output" + str(i)
		src_file_names.append(temp_out)
		cmd += "--inference_output_file=" + temp_out
		print(cmd)
		os.system(cmd)
	outf = open(args.output + "merged_output", "w")
	
	for name in src_file_names:
		src_files.append(open(name, "r"))
	isEnd = False
	while isEnd == False:
		for f in src_files:
			line = f.readline()
			if line == None or len(line) == 0:
				isEnd = True
				break
			outf.write(line)
			
	for f in src_files:
		f.close()
	for fn in src_file_names:
		os.system("rm "+fn)
	outf.close()
