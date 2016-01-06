#!/usr/bin/env python

import argparse
from itertools import chain
import sys

import fastavro as avro

parser = argparse.ArgumentParser(description='Extracts fields from avro-files to tsv lines')
parser.add_argument('filenames', nargs='+', help='if extension of file is .lst or .txt it will be assumed to be a file of filenames')
parser.add_argument('-f', '--field', nargs='*', help='Field to extract')
parser.add_argument('-l', '--list-fields', action='store_true', help='List fields in files')

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

def _extract(some_record, field_names):
    result = some_record
    for f in field_names:
        result = result.get(f, {})
    return result if not isinstance(result,dict) else "FieldNotFound"

def extract(some_record, fields):
    print '\t'.join( str(_extract(some_record,f)) for f in fields )

global_fields = tuple( f.split('/') for f in args.field or () )
for filename in chain.from_iterable( expand(f) for f in args.filenames ):
    print >> sys.stderr, "Processing " + filename
    with open(filename, 'rb') as avro_file:
        reader = avro.reader(avro_file)
        schema = reader.schema
        fields = global_fields
        for index, record in enumerate(reader):
            if not fields:
                fields = tuple(get_fields(record))
            if args.list_fields:
                print 'Fields in %s:' % (filename,)
                for f in fields:
                    print '  Field: ' + '/'.join(f)
                break
            if index and not (index % 1000):
                sys.stderr.write("Read %d lines of input\r" % (index,))
            extract(record, fields)
        print >> sys.stderr, "Read %d lines of input\r" % (index,)


