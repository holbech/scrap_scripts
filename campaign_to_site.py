#!/usr/bin/env python

from itertools import groupby
import sys

def split_line(line):
    try:
        parts = line.rstrip('\n').split('\t')
        if 'NO_ENTITY_MARKER' in parts[1]:
            parts[1] = (parts[1],)
        else:
            parts[1] = (parts[1].split(',', 1)[0], parts[1].rsplit(',',1)[1])
        return parts
    except Exception:
        print line
        raise

if __name__ == "__main__":
    split_lines = ( split_line(l) for l in open(sys.argv[1], 'r') )
    for site_customer, lines in groupby(split_lines, key=lambda l: l[1]):
        lines = list(lines)
        best = max(( l for l in lines ), key=lambda l: (len(l[2]), int(l[3])) )
        best[0] = 'user_on_site.last_product_seen'
        best[1] = ','.join(best[1])
        print '\t'.join(best)

