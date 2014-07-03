#!/usr/bin/env python

if __name__ == "__main__":
    import sys
    import os
    import gzip
    import shutil
    import tempfile
    filter_file = sys.argv[1]
    if filter_file.startswith('-'):
        reverse = True
        filter_file = filter_file[1:]
    else:
        reverse = False
    filter_strings = tuple( l.strip() for l in open(filter_file, 'r').readlines() if l.strip() )
    for file_name in sys.argv[2:]:
        print "Filtering " + file_name
        lines_copied = 0
        with tempfile.TemporaryFile() as temp_file:
            with open(file_name, 'r') as input_file:
                for l in input_file:
                    matches = any( filter_str in l for filter_str in filter_strings )
                    if matches != reverse:
                        temp_file.write(l)
                        lines_copied += 1
            temp_file.seek(0)
            with open(file_name, 'w') as output_file:
                shutil.copyfileobj(temp_file, output_file)
        print "Kept " + str(lines_copied) + " lines of " + file_name

