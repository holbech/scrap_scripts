#!/usr/bin/env python

import gzip
import os
import sys
import urllib

input_file = sys.argv[1]
output_dir = sys.argv[2]
column = int(sys.argv[3])

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with gzip.GzipFile(input_file) if input_file.endswith('.gz') else open(input_file) as in_file:
    current_column_value = None
    out_file = None
    for line in in_file:
        col_value = line.split('\t')[column]
        if col_value != current_column_value:
            print 'Writing', col_value
            if out_file:
                out_file.close()
            out_file_name = os.path.join(output_dir, urllib.pathname2url(col_value))
            if os.path.exists(out_file_name):
                raise ValueError(out_file_name + ' exists. Is input file not sorted?')
            out_file = open(out_file_name, 'w')
            current_column_value = col_value
        out_file.write(line)
