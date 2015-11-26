#!/usr/bin/env python

if __name__ == "__main__":
    import sys
    import math
    import os
    import gzip
    import shutil
    import subprocess
    import tempfile
    import time
    filter_file = sys.argv[1]
    if filter_file.startswith('-'):
        reverse = True
        filter_file = filter_file[1:]
    else:
        reverse = False
    filter_strings = tuple( l.strip() for l in open(filter_file, 'r').readlines() if l.strip() )
    for file_name in sys.argv[2:]:
        print "Filtering " + file_name
        lines = 0
        lines_step = 10
        lines_copied = 0
        start_time = time.time()
        with tempfile.TemporaryFile() as temp_file:
            with open(file_name, 'r') as input_file:
                for i,l in enumerate(input_file):
                    if i and i % lines_step == 0:
                        if not lines:
                            lines = int(subprocess.check_output('wc -l ' + file_name, shell=True).split()[0])
                            lines_step = max(10, lines/100)
                            if lines > 10:
                                lines_step = round(lines_step, -int(math.log10(lines_step)))
                        sys.stdout.write(('\r' if i > 10 else '') + '%d/%d' % (i, lines))
                        sys.stdout.flush()
                    matches = any( s in l for s in filter_strings )
                    if matches != reverse:
                        temp_file.write(l)
                        lines_copied += 1
            temp_file.seek(0)
            with open(file_name, 'w') as output_file:
                shutil.copyfileobj(temp_file, output_file)
        print ('\r' if lines else '') + "Kept " + str(lines_copied) + " lines of " + file_name + '. Time taken: %0.2f' % (time.time() - start_time,)

