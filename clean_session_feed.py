import sys

if __name__ == "__main__":
    for line in open(sys.argv[1], 'r'):
        print line.partition('\a')[0] + '\tLG1XJ\t'
