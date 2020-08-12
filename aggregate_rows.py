#!/usr/bin/env python

from collections import defaultdict
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

import sys
import argparse

parser = argparse.ArgumentParser(description='Aggregates (sums) rows based on fixed values of other rows')
parser.add_argument('aggregations', type=int, nargs='+', help='Column to aggregate')
parser.add_argument('-f', '--fixed', type=int, nargs='*', help='Columns to fix')
parser.add_argument('-d', '--delimiter', type=str, help='Columns separator', default='\t')

args = parser.parse_args()



result = defaultdict(lambda: (0.0,)*len(args.aggregations))

for line in sys.stdin:
    l = dict(enumerate(line.rstrip('\n').split(args.delimiter)))
    key = args.delimiter.join( l[c - 1] for c in args.fixed )
    result[key] = tuple( a + float(b or 0.0) for (a,b) in zip(result[key], ( l[c - 1] for c in args.aggregations )) )

if len(result) == 1:
    sys.stdout.write(args.delimiter.join( str(v) for v in next(result.itervalues()) ) + '\n')
else:
    sys.stdout.writelines( k + args.delimiter + args.delimiter.join( str(v) for v in vs ) + '\n'
                           for k,vs in sorted(result.iteritems()) )

