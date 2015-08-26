#!/usr/bin/env python

from collections import defaultdict
import os
import subprocess
import sys

if __name__ == "__main__":
    eval_path = os.path.join(os.path.dirname(__file__), 'eval.sh')
    eval_path = "/home/holbech/Desktop/exps/eval.sh"
    
    assert len(sys.argv) > 2, "Supply the names of at least two files to this script"

    def run_eval(mapping_file):
        print "Evaluating: " + mapping_file
        output = subprocess.check_output([eval_path, mapping_file])
        return [ l.partition(':')[2].strip().partition(':') for l in output.splitlines() if l.startswith('Result:') ]
    
    mapping_files = [ fn for fn in sys.argv[1:] if not fn.endswith('_rankings') ]
    prefix_length = len(os.path.commonprefix(mapping_files))
    mapping_titles = [ fn[prefix_length:] for fn in mapping_files ]
    
    def pretty_print(matrix):
        print '\n\t' + '\t'.join(mapping_titles)
        for row_type, values in sorted(matrix.iteritems()):
            print str(row_type) + '\t' + '\t'.join( str(values[f]) for f in mapping_files )
        
    results = [ (f, run_eval(f)) for f in mapping_files ]
    results_matrix = defaultdict(lambda : defaultdict(lambda : '?'))
    for fn, r in results:
        for (t,_,v) in r:
            results_matrix[t][fn] = v
    
    print "Scalar metrics:"
    pretty_print(results_matrix)
    
    ranking_matrix = defaultdict(lambda : defaultdict(int))
    for i, f in enumerate(mapping_files):
        with open(f + '_rankings') as ranking_file:
            for l in ranking_file:
                l = l.split('\t')
                assert len(l) == 2, "Strange line in %s: %s" % (f + '_rankings', '\t'.join(l))
                ranking_matrix[int(l[0])][f] = int(l[1])
    
    print "Ranking matrix:"
    pretty_print(ranking_matrix)
    
    
    
