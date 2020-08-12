#!/usr/bin/env python
import csv
import sys
import argparse

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser(description='Adds/replaces mapping types with waterfall number')
parser.add_argument('column', type=int, help='Column to read')
parser.add_argument('-a', '--append', action='store_true', help='Append new column rather than replace existing one')
parser.add_argument('-i', '--ignore-errors', action='store_true', help='Ignore unknown mapping type lookups')
parser.add_argument('-r', '--reverse', action='store_true', help='Reverse priority of mapping types')
parser.add_argument('-d', '--delimiter', default='\t', help='Delimiter between columns')
parser.add_argument('-t', '--translate', action='store_true', help='Translate list of mapping types instead of prioritizing')

args = parser.parse_args()

def read_csv():
    r = csv.reader(sys.stdin)
    while True:
        yield r.next()

def read_other():
    for l in sys.stdin:
        yield l.rstrip('\n').split(args.delimiter)


mt_column = args.column - 1 

wf =  {
 'd/click': 1,
 'd/eopen': 1,
 'd/esp': 1,
 'd/imp': 1,
 'd/imps': 1,
 'd/iopen': 1,
 '3m': 4,
 'acc': 4,
 'accx': 3,
 'd/sourced': 2,
 'd/weblogin':1,
 'lrxd': 2,
 'max': 5
}

wf =  {
 'd/click': 2,
 'd/eopen': 2,
 'd/esp': 2,
 'd/imp': 2,
 'd/imps': 2,
 'd/iopen': 2,
 '3m': 3,
 'acc': 3,
 'accx': 3,
 'd/sourced': 1,
 'd/weblogin':2,
 'lrxd': 1,
 'max': 3
}


none_value = str(max(wf.itervalues()) + 1)

if args.translate:
    prioritize = lambda vs: ','.join(sorted({ str(v) for v in vs }))
else:
    prioritize = max if args.reverse else min


for (i,l) in enumerate(read_csv() if args.delimiter==',' else read_other()):
    try:
        new_value = none_value if not l[mt_column] else str(prioritize( wf[m] for m in l[mt_column].split(',') ))
    except KeyError:
        if i == 0:
            new_value = l[mt_column]
        elif args.ignore_errors:
            new_value = ''
        else:
            raise
    if args.append:
        l.append(new_value)
    else:
        l[mt_column] = new_value
    sys.stdout.write('\t'.join(l) + '\n')
    
