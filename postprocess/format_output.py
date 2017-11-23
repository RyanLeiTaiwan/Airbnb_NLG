# Format Seq2Seq output by merging input, reference, and NLG files, assuming we generate N descriptions per input line
"""
[Merged format]
input: xxx
ref: xxx
nlg:
1. xxx
2. xxx
3. xxx
...
"""
import argparse

def build_parser():
    parser = argparse.ArgumentParser(description='Format output by merging input, reference, NLG files.')
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Data input file (.data)'
    )
    parser.add_argument(
        '-r', '--ref',
        required=True,
        help='Reference file (.desc)'
    )
    parser.add_argument(
        '-n', '--nlg',
        required=True,
        help='NLG output file'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output merged file'
    )
    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        input = f.read().splitlines()
        lines_input = len(input)
    print 'input: %d lines' % lines_input

    with open(args.ref, 'r') as f:
        ref = f.read().splitlines()
        lines_ref = len(ref)
    print 'ref: %d lines' % lines_ref

    assert lines_input == lines_ref

    with open(args.nlg, 'r') as f:
        nlg = f.read().splitlines()
        lines_nlg = len(nlg)
    print 'nlg: %d lines' % lines_nlg

    # Make sure len_nlg is an integer multiple of len_input
    nlg_lines_per_input = lines_nlg // lines_input
    assert lines_input * nlg_lines_per_input == lines_nlg
    print '=> %d nlg lines per input line' % nlg_lines_per_input

    with open(args.output, 'w') as f:
        # For each property
        for prop in range(lines_input):
            # For each description in beam search or greedy sampling results
            f.write('INPUT: %s\n' % input[prop])
            f.write('REF: %s\n' % ref[prop])
            f.write('NLG:\n')
            for desc in range(nlg_lines_per_input):
                f.write('%2d. %s\n' % (desc + 1, nlg[nlg_lines_per_input * prop + desc]))
            f.write('=' * 80 + '\n')

    print 'Finished writing the merged file to %s' % args.output
