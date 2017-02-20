import sys

def fix(line, time):
    result = ':'.join( '%02d' % (int(t,)) for t in time.split(':') )
    if result.strip() != time.strip():
        sys.stderr.writelines(time)
    return result

if __name__ == "__main__":
    for line in open(sys.argv[1], 'r'):
        split_line = line.split('\t')
        print '\t'.join(split_line[:-1] + [fix(line, split_line[-1])])
