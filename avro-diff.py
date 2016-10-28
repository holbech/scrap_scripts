#!/usr/bin/env python

import json
import sys

schema1 = json.load(open(sys.argv[1]))
schema2 = json.load(open(sys.argv[2]))
def print_cross (s1set, s2set, message):
    for s in s1set:
        if not s in s2set:
            print message % s
s1names = set( [ field['name'] for field in schema1['fields'] ] )
s2names = set( [ field['name'] for field in schema2['fields'] ] )
print_cross(s1names, s2names, 'Field "%%s" exists in %s and does not exist in %s' % (sys.argv[1], sys.argv[2]))
print_cross(s2names, s1names, 'Field "%%s" exists in %s and does not exist in %s' % (sys.argv[2], sys.argv[1]))
def print_cross2 (s1dict, s2dict, message):
    for s in s1dict:
        if s in s2dict:
            if s1dict[s] != s2dict[s]:
                print message % (s, s1dict[s], s2dict[s])
s1types = dict( zip( [ field['name'] for field in schema1['fields'] ],  [ str(field['type']) for field in schema1['fields'] ] ) )
s2types = dict( zip( [ field['name'] for field in schema2['fields'] ],  [ str(field['type']) for field in schema2['fields'] ] ) )
print_cross2 (s1types, s2types, 'Field "%%s" has type "%%s" in %s and type "%%s" in %s' % (sys.argv[1], sys.argv[1]))
