#!/usr/bin/env python

import argparse
from functional import seq
import sys
from itertools import (chain,
                       groupby,
                       product)
from operator import itemgetter

parser = argparse.ArgumentParser(description='Transposes rows into columns')
parser.add_argument('-c', '--count-column', type=int, default=0, help='Column to use for counts (counts are 1 if not supplied)')
parser.add_argument('value_columns', type=int, nargs='+', help='Columns to transpose values of')
parser.add_argument('-d', '--delimiter', default='\t', help='Delimiter between columns')
parser.add_argument('-v', '--value-delimiter', default='', help='Delimiter between sub-values')
parser.add_argument('-vc', '--value-concatenator', default='/', help='Concatenator for synthesized values')
parser.add_argument('-ah', '--add-header', action='store_true', help='Input has no header - add one')

def read_csv():
    import csv
    r = csv.reader(sys.stdin)
    while True:
        yield r.next()

def read_other():
    for l in sys.stdin:
        yield l.rstrip('\n').split(args.delimiter)
        
args = parser.parse_args()

value_columns = sorted({ a - 1 for a in args.value_columns })

count_column = args.count_column - 1 

dataset = seq(read_csv() if args.delimiter==',' else read_other())

header = [ '' if args.add_header else p for i,p in enumerate(dataset[0]) if i != count_column and i not in value_columns ] 

dataset = dataset if args.add_header else dataset[1:]

fixed_indices = [ i for i,_ in enumerate(dataset[0]) if i != count_column and i not in value_columns ]

if args.value_delimiter:
    def get_values(row):
        return { jv for jv in ( args.value_concatenator.join(v) for v in product(*[ row[c].split(args.value_delimiter) for c in value_columns ]) ) if jv }
else:
    def get_values(row):
        result = args.value_concatenator.join( row[c] for c in value_columns )
        return {result} if result else set()

try:
    values = sorted(set(chain.from_iterable( get_values(d) for d in dataset )))
except IndexError:
    header_width = len(header)
    for i,d in enumerate(dataset):
        if len(d) < header_width:
            raise IndexError('Row %d has too few members: %s' % (i, ', '.join(d)))
    raise

header.extend(values)

def get_value_tuple(rows, key):
    rows = list( (get_values(r), r[count_column] if count_column >= 0 else '1') for r in rows )
    pairs = sorted( (i, r[1]) for i,v in enumerate(values) for r in rows if v in r[0] )
    for g,vs in groupby(pairs,key=itemgetter(0)):
        if len(set(vs)) > 1:
            raise RuntimeError('Rows for group (%s) has conflicting counts for value %s: %s' % (', '.join(key), values[g], '!='.join(sorted(set(vs)))))
    pairs = dict(pairs)
    return tuple( pairs.get(i, "") for i,_ in enumerate(values) )
    

data = dataset.group_by(lambda d: tuple( d[i] for i in fixed_indices ) )\
              .map(lambda key_rows: key_rows[0] + get_value_tuple(key_rows[1], key_rows[0]) )

sys.stdout.writelines( '\t'.join(l) + '\n' for l in seq((header,)) + data ) 

