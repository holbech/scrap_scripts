#!/usr/bin/env python

from itertools import groupby
from operator import itemgetter
import shutil
import sys
import tempfile

with open(sys.argv[1]) as unused_lines:
    changes = ( line.split('/',1)[1].split(' ', 1)[0].split(':') for line in unused_lines )
    for filename, needed_deletions in groupby(changes, key=itemgetter(0)):
        filename = '/' + filename
        print "Processing", filename
        needed_deletions = { int(nd[1]) - 1 for nd in needed_deletions }
        print "Removing", needed_deletions
        tmp_filename = None
        with tempfile.NamedTemporaryFile('w', delete=False) as output:
            tmp_filename = output.name
            with open(filename) as input:
                output.writelines( l for (i,l) in enumerate(input) if '{' in l or i not in needed_deletions )
        shutil.copy(tmp_filename, filename)

