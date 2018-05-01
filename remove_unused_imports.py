#!/usr/bin/env python

from itertools import groupby
from operator import itemgetter
import shutil
import sys
import tempfile
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def get_changes(compile_lines):
    previous = None
    previous_previous = None
    for l in compile_lines:
        l = ansi_escape.sub('', l.strip())
        if l.strip().endswith('Unused import'):
            previous = l
            previous_previous = None
        elif previous_previous:
            if '{' in previous:
                print 'Cannot automatically fix:'
                print previous_previous
                print previous
                print l
            else:
                print 'Fixing ' + previous_previous
                yield previous_previous
            previous = None
            previous_previous = None
        elif previous:
            previous_previous = previous
            previous = l
        else:
            previous = None
            previous_previous = None

with open(sys.argv[1]) as compilation_output:
    changes = ( line.split('/',1)[1].split(' ', 1)[0].split(':') for line in get_changes(compilation_output) )
    for filename, needed_deletions in groupby(changes, key=itemgetter(0)):
        filename = '/' + filename
        print "Processing", filename
        needed_deletions = { int(nd[1]) - 1 for nd in needed_deletions }
        print "Removing", needed_deletions
        tmp_filename = None
        with tempfile.NamedTemporaryFile('w', delete=False) as output:
            tmp_filename = output.name
            with open(filename) as input:
                output.writelines( l for (i,l) in enumerate(input) if i not in needed_deletions )
        shutil.copy(tmp_filename, filename)

