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
import sys

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print 'Usage: %s INPUT_FILE REF_FILE NLG_FILE MERGED_FILE' % sys.argv[0]
        print 'Example: %s test_set.data test_set.desc test_set.out merged.txt'
        exit(0)

    with open(sys.argv[1], 'r') as f:
        input = f.read().splitlines()
        lines_input = len(input)
    print 'input: %d lines' % lines_input

    with open(sys.argv[2], 'r') as f:
        ref = f.read().splitlines()
        lines_ref = len(ref)
    print 'ref: %d lines' % lines_ref

    assert lines_input == lines_ref

    with open(sys.argv[3], 'r') as f:
        nlg = f.read().splitlines()
        lines_nlg = len(nlg)
    print 'nlg: %d lines' % lines_nlg

    # Make sure len_nlg is an integer multiple of len_input
    nlg_lines_per_input = lines_nlg // lines_input
    assert lines_input * nlg_lines_per_input == lines_nlg
    print '=> %d nlg lines per input line' % nlg_lines_per_input

    with open(sys.argv[4], 'w') as f:
        # For each property
        for prop in range(lines_input):
            # For each description in beam search or greedy sampling results
            f.write('intput: %s\n' % input[prop])
            f.write('ref: %s\n' % ref[prop])
            f.write('nlg:\n')
            for desc in range(nlg_lines_per_input):
                f.writelines('%2d. %s\n' % (desc + 1, nlg[nlg_lines_per_input * prop + desc]))
            f.write('\n')

    print 'Finished writing the merged file to %s' % sys.argv[4]