#!/usr/bin/env python

import argparse
from collections import defaultdict
from itertools import chain
import sys
from multiprocessing import Pool

import fastavro as avro

parser = argparse.ArgumentParser(description='Extracts fields from avro-files to tsv lines')
parser.add_argument('filenames', nargs='+', help='if extension of file is .lst or .txt it will be assumed to be a file of filenames')
parser.add_argument('-m', '--multiprocessing', type=int, default=1, help='Parallel processes to run')
parser.add_argument('-f', '--field', nargs='*', help='Field to extract')
parser.add_argument('-l', '--list-fields', action='store_true', help='List fields in files')
parser.add_argument('-a', '--add-header', action='store_true', help='Add field names as header to output')
parser.add_argument('-s', '--sample-values', type=int, default=0, help='If larger than zero, list each field in files along with this number of sample values')

args = parser.parse_args()

def get_fields(some_record):
    for k,v in some_record.iteritems():
        if isinstance(v, dict):
            for sf in get_fields(v):
                yield (k,) + sf
        else:
            yield (k,)

def expand(input_filename):
    if input_filename.endswith(('.txt', '.lst')):
        with open(input_filename, 'r') as files:
            for l in files:
                yield l.strip()
    else:
        yield input_filename

class SampleCollector(object):
    def __init__(self):
        self._values = set()
        self.is_full = False
    def add(self, value):
        if not self.is_full:
            self._values.add(value)
            self.is_full = len(self._values) == args.sample_values
    def __iter__(self):
        return iter(self._values)

samples = (args.sample_values or None) and defaultdict(SampleCollector)

def _format(value):
    if value is None:
        return ""
    if isinstance(value, basestring):
        return value
    try:
        return ujson.dumps(value)
    except:
        if isinstance(value, (tuple, list)):
            return '[' + ','.join( _format(v) for v in value ) + ']'
        if isinstance(value, dict):
            return '{' + ','.join( _format(v) for v in value ) + '}'
        if not isinstance(value, basestring):
            return str(value)

NOT_FOUND = object()

def _extract(some_record, field_names):
    result = some_record
    for f in field_names:
        result = result.get(f, NOT_FOUND)
    if result is not NOT_FOUND:
        result = _format(result)
        result = result.replace('\t','\\t').replace('\n','\\n')
        if isinstance(result, unicode):
            result = result.encode('utf-8')
        if samples is not None and result:
            samples[field_names].add(result)
        return result  
    else:
        return "FieldNotFound"

def extract(some_record, fields):
    return [ _extract(some_record, f) for f in fields ]

global_fields = tuple( f.split('/') for f in args.field or () )
def extract_file(filename):
    print >> sys.stderr, "Processing " + filename
    result = []
    with open(filename, 'rb') as avro_file:
        reader = avro.reader(avro_file)
        schema = reader.schema
        fields = global_fields
        add_header = args.add_header
        for index, record in enumerate(reader):
            if not fields:
                fields = tuple(get_fields(record))
            if args.list_fields:
                print 'Fields in %s:' % (filename,)
                for f in fields:
                    print '  Field: ' + '/'.join(f)
                break
            if add_header:
                print '\t'.join( '/'.join( p.encode('utf-8') for p in f ) for f in fields )
                add_header = False
            if index and not (index % 1000):
                if samples and all( s.is_full for s in samples.itervalues() ):
                    break
                sys.stderr.write("Read %d lines of input\r" % (index,))
            extracted_values = extract(record, fields)
            if samples is None:
                result.append('\t'.join(extracted_values))
        if samples:
            print 'Samples values from %s:' % (filename,)
            for f in fields:
                print '  ' + '/'.join(f) + ':'
                for v in sorted(samples[f]):
                    print '    ' + v
        print >> sys.stderr, "Read %d lines of input\r" % (index,)
    return result

filenames = chain.from_iterable( expand(f) for f in args.filenames )
if args.multiprocessing > 1 and not args.sample_values:
    if args.add_header:
        sys.stdout.writelines( l + '\n' for l in extract_file(next(filenames)) )
    pool = Pool(args.multiprocessing)
    sys.stdout.writelines( l + '\n' for l in chain.from_iterable(pool.imap_unordered(extract_file, filenames, chunksize=1)) )
else:
    for fn in filenames:
        sys.stdout.writelines( l + '\n' for l in extract_file(fn) )
