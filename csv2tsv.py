#!/usr/bin/env python

import re

counts = set()

parts_extractor = re.compile(r'(?:(?:[^,"]*)|(?:[^,"][^,]*)|(?:"(?:(?:(?:\\"|[^\\"])+?)(?:\\\\)*")))(?:,|$)')

def convert(line):
    result = parts_extractor.findall(line)
    if len(result) > 1 and not result[-2].endswith(','):
        result = result[:-1]
    seps = len(result)
    if counts and seps not in counts:
        print >> sys.stderr, "First strange line:", line
    counts.add(seps)
    return '\t'.join( r.rstrip(',') for r in result )

if __name__ == '__main__':
    import sys
    import gzip
    with (gzip.open if sys.argv[1].endswith('.gz') else open)(sys.argv[1]) as input:
        sys.stdout.writelines( convert(l) for l in input )
    if len(counts) > 1:
        print >> sys.stderr, "Uneven counts of tab-separators in output", ', '.join( str(i) for i in sorted(counts) )
        