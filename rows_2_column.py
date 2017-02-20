#!/usr/bin/env python

from functional import seq
import sys

group_column = int(sys.argv[1]) - 1 

value_column = int(sys.argv[2]) - 1 

dataset = seq([ line.rstrip('\n').split('\t') for line in sys.stdin if line.strip() ])

remaining_indices = [ i for i,_ in enumerate(dataset[0]) if i not in (group_column, value_column) ]

values = sorted({ d[group_column] for d in dataset[1:] })

header = [ p for i,p in enumerate(dataset[0]) if i not in (group_column, value_column) ] + values

def get_value_tuple(rows):
    rows = list(rows)
    pairs = { i: r[value_column] for i,v in enumerate(values) for r in rows if r[group_column] == v }
    return tuple( pairs.get(i, "") for i,_ in enumerate(values) )
    

data = dataset[1:].group_by(lambda d: tuple( d[i] for i in remaining_indices ) )\
                  .map(lambda key_rows: key_rows[0] + get_value_tuple(key_rows[1]) )

sys.stdout.writelines( '\t'.join(l) + '\n' for l in seq((header,)) + data ) 

