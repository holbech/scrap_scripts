import argparse
import fnmatch
import math
import random
import sys

def partial_resolver(input_value):
    if input_value.lower() in ('ceil', 'floor', 'round', 'random'):
        return input_value.lower()
    input_value = float(input_value)
    assert 0.0 < input_value < 1.0, 'Cutoff must be between 0 and 1'
    return input_value

class Filter(object):
    def __init__(self, definition):
        self.column, _, acceptance = definition.partition('=')
        self._call = eval("lambda x: " + acceptance.replace("{}", "x"))
    def __call__(self, x):
        return self._call(x)

class Field(object):
    def __init__(self, definition):
        self.matcher, _, self.orange_type = definition.partition('=')
        self._resolved = False
        self.orange_type_prefix = self.orange_type + '#'
    def __call__(self, column_name):
        result = fnmatch.fnmatch(column_name, self.matcher)
        self._resolved |= result
        return result
    def __nonzero__(self):
        return self._resolved

parser = argparse.ArgumentParser(description='Unaggregates uPredict aggregates for further analysis in standard tools')
parser.add_argument('filename', nargs='?', default= '-', help='if unspecified or "-" use stdin')
parser.add_argument('-f', '--field', nargs='*', type=Field, help='Fields to output')
parser.add_argument('-t', '--tries', type=str, required=True, help='Tries field')
parser.add_argument('-s', '--success', type=str, required=True, help='Success field')
parser.add_argument('-r', '--resolver', type=partial_resolver, default='ceil', help='Resolver of partial cases: "ceil", "floor", "round", "random" or a float between 0 and 1')
parser.add_argument('--random', type=int, default='1234', help='Seed for random generator')
parser.add_argument('-n', '--no-header', action='store_true', help='Do not add field names as header to output')
parser.add_argument('--sample-rate', type=float, default=1.0)
parser.add_argument('--filter', nargs='*', type=Filter, help='Column filter')

args = parser.parse_args()

input_file = open(args.filename) if args.filename != '-' else sys.stdin

random = random.Random(args.random)

if args.resolver == 'random':
    def resolve(some_float):
        floor = int(math.floor(some_float)) 
        return floor + bool(some_float - floor > r.random())
elif isinstance(args.resolver, str):
    def resolve(some_float):
        return int(getattr(math, args.resolver)(some_float))
else:
    def resolve(some_float):
        floor = int(math.floor(some_float)) 
        return  floor + bool(some_float - floor > args.resolver)

columns = None
filters = None
try:
    tries = int(args.tries)
except ValueError:
    tries = None
try:
    success = int(args.success)
except ValueError:
    success = None
sample_rate = args.sample_rate if args.sample_rate < 1.0 else True
for line in input_file:
    line = line.rstrip('\n').split('\t')
    if columns is None:
        column_names = ( (i, next(( f for f in (args.field or Field('*')) if f(v) ), None)) for i,v in enumerate(line) )
        column_names = { i: f for i,f in column_names if f is not None }
        for f in args.field:
            if not f:
                raise ValueError('Found no column matching %s. Column names are %s' % (f.matcher, ', '.join(line)))
        columns = sorted( i for (i,f) in column_names.iteritems() if f )
        try:
            tries = tries if tries is not None else line.index(args.tries)
            success = success if success is not None else line.index(args.success)
        except ValueError as ex:
            raise ValueError(ex.message + ' - Columns are ' + ', '.join(line)) 
        if not args.no_header:
            print '\t'.join( tuple( column_names[i].orange_type_prefix + line[i] for i in columns ) + (('cD#' if any(f.orange_type for f in column_names.itervalues() ) else '') + 'is_success',))
        filters = ( (i, next(( f for f in args.filter if f.column.lower() == v.lower() ), None)) for i,v in enumerate(line) )
        filters = tuple( (i,f) for i,f in filters if f is not None )
        for f in args.filter:
            if f not in { u for (i,u) in filters }:
                raise ValueError('Found no column matching %s. Column names are %s' % (f.column, ', '.join(line)))
        continue
    if filters and not any( f(line[i]) for (i,f) in filters ):
        continue
    successes = int(line[success])
    tries_count = resolve(float(line[tries]))
    values = '\t'.join( line[v] for v in columns )
    new_lines = []
    if successes:
        new_lines.extend((values + '\ty',)*successes)
    if tries_count > successes:
        new_lines.extend((values + '\tn',)*(tries_count-successes))
    new_lines = tuple( l for l in new_lines if sample_rate is True or random.random() < args.sample_rate )
    if new_lines:
        print '\n'.join(new_lines)
