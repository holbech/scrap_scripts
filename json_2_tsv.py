#!/usr/bin/env python

if __name__ == '__main__':
    import argparse
    import sys
    import json
    from itertools import chain

    parser = argparse.ArgumentParser(description='Converts nested json lines to tsv lines')
    parser.add_argument('filename', default='-', help='- or missing for stdin')
    parser.add_argument('-im', '--ignore-missing', action='store_true', help='Ignores missing values from lines')
    parser.add_argument('-is', '--ignore-surplus', action='store_true', help='Ignores extra values from lines')
    parser.add_argument('-n', '--no-header', action='store_true', help='Do not print a header line')
    parser.add_argument('-s', '--scheme-file', help='File to read scheme from (scheme is inferred from first line if not given)')
    parser.add_argument('-o', '--orange-tags', action='store_true', help='Add tags to header that allows import into Orange')
    parser.add_argument('-d', '--distribution', nargs='*', help='Keysets (e.g. "device_type/details/") to convert to multinomial distributions')
    parser.add_argument('-f', '--field', type=int, default=-1, help='Work on field number rather than entire line')
    parser.add_argument('-of', '--output-file', type=argparse.FileType('w'), help='Output to this file rather than stdout')
    parser.add_argument('-df', '--default', nargs='*', help='Defaults for keys (e.g. "device_type/details/Smartphone=24")')
    parser.add_argument('--infer-scheme', action='store_true', help='Infer scheme from all observations and store result in --scheme-file')
    parser.add_argument('--print-scheme', action='store_true', help='Print scheme in --scheme-file')
    parser.add_argument('-u', '--add-unparsed', action='store_true', help='Add column with unparsed value if no values could be extracted')
    parser.add_argument('-hn', '--header-name', nargs='*', help='Name for a header of a specific column (e.g. 3=ip)')
    
    args = parser.parse_args()

    def orange_tag(value):
        if not args.orange_tags:
            return ''
        if isinstance(value, basestring):
            if value == "D#":
                return "D#"
            return "S#"
        else:
            return "C#"

    class Scheme(object):

        def _scrape_keys(self, parsed_json, path=''):
            if isinstance(parsed_json, (list, tuple)):
                raise ValueError('Cannot read json with sequence elements')
            if isinstance(parsed_json, dict):
                return chain(( path + '/' + k for k,v in parsed_json.iteritems() if not isinstance(v, dict) ),
                             chain.from_iterable( self._scrape_keys(v, path + '/' + k)
                                                  for k,v in parsed_json.iteritems() if isinstance(v, dict) ))
            return ()
    
        def __init__(self, parsed_json):
            values = self._flatten(parsed_json) if args.orange_tags else {}
            self._keys = [ (k, orange_tag(values.get(k, "")))
                           for k in sorted( ik[1:] for ik in self._scrape_keys(parsed_json) ) ]
            self._defaults = dict( d.split('=',1) for d in args.default or () )

        def _extract(self, parsed_json, path=''):
            if isinstance(parsed_json, dict):
                yield (path, dict)
                for e in chain.from_iterable( self._extract(v, path + '/' + k) for k,v in parsed_json.iteritems() ):
                    yield e
            else:
                yield (path, parsed_json)

        def _flatten(self, parsed_json):
            return { k[1:]: v for k,v in self._extract(parsed_json) }

        _missing_marker = object()

        def __call__(self, parsed_json):
            flattened = self._flatten(parsed_json)
            for distribution_set in args.distribution or ():
                flattened_subset = tuple( (k,v) for k,v in flattened.iteritems() if k.startswith(distribution_set) and k != distribution_set )
                sum_subset = sum( v for (_,v) in flattened_subset )
                flattened.update( (k,float(v)/(sum_subset or 1)) for (k,v) in flattened_subset )
            found_keys = set()
            at_least_one_found = False
            for (k,_) in self._keys:
                result = flattened.pop(k, self._missing_marker)
                if (result not in (dict, self._missing_marker)):
                    yield result
                    at_least_one_found = True
                    k = k.split('/')
                    while k:
                        found_keys.add('/'.join(k))
                        k = k[0:-1]
                elif result is dict:
                    raise ValueError('%s is a container in %s' % (k, json.dumps(parsed_json))) # pylint: disable=E1101
                elif args.ignore_missing or k in self._defaults:
                    yield self._defaults.get(k, "")
                    k = k.split('/')
                    while k:
                        found_keys.add('/'.join(k))
                        k = k[0:-1]
                else:
                    raise ValueError('Cannot extract %s from %s' % (k, json.dumps(parsed_json))) # pylint: disable=E1101
            if args.add_unparsed:
                yield '' if at_least_one_found else json.dumps(parsed_json)
            if (not args.ignore_surplus):
                flattened = ', '.join( '%s: %s' % (k, str(v)) for k,v in flattened.iteritems() if v and (v is not dict) and k not in found_keys )
                if flattened:
                    raise ValueError('Found extra values ' + flattened)
    
        def get_headers(self):
            return chain(( ot + k for (k,ot) in self._keys ), ('unparsed',) if args.add_unparsed else ())

    
    def update(some_dict, some_key, some_value, path=''):
        path = path or ('/' + some_key)
        current_value = some_dict.get(some_key)
        if isinstance(current_value, dict):
            if isinstance(some_value, dict):
                for k,v in some_value.iteritems():
                    update(current_value, k, v, path + '/' + k)
            elif some_value is not None and not isinstance(some_value, basestring):
                print "Warning: Type of %s jumped from dict to %s" % (path, str(type(some_value)))
        elif isinstance(some_value, dict):
            some_dict[some_key] = {}
            for k,v in some_value.iteritems():
                update(some_dict[some_key], k, v, path + '/' + k)
            if current_value is not None and not isinstance(current_value, (set, basestring)):
                print "Warning: Type of %s jumped from %s to dict" % (path, str(type(current_value)))
        elif current_value is None:
            some_dict[some_key] = { some_value } if isinstance(some_value, basestring) else some_value
        elif isinstance(current_value, set) and isinstance(some_value, basestring):
            current_value.add(some_value)
            if len(current_value) > 10:
                some_dict[some_key] = some_value
        elif isinstance(current_value, (set, basestring)):
            if not isinstance(some_value, basestring):
                if some_value is not None:
                    print "Warning: Type of %s jumped from string to %s" % (path, str(type(some_value)))
                    some_dict[some_key] = some_value
        elif type(current_value) != type(some_value):
            if some_value is not None:
                print "Warning: Type of %s jumped from %s to %s" % (path, str(type(current_value)), str(type(some_value)))
    
    def clear_values(some_dict, path=''):
        for k,v in list(some_dict.iteritems()):
            if isinstance(v, dict):
                clear_values(v, path + '/' + k)
            elif isinstance(v, set):
                some_dict[k] = 'D#'
            elif v is None or isinstance(v, basestring):
                some_dict[k] = ""
            elif isinstance(v, (int,float)):
                some_dict[k] = 0
            else:
                print "Warning: Ended up with a value of type %s (%s) at %s in cleared dict" % (str(type(v)), str(v), path + '/' + k)
    
    def infer_scheme():
        with open(args.scheme_file, 'w') as scheme_file:
            scheme_object = {}
            headers = []
            header_names = ( hn.split('=') for hn in args.header_name or () )
            header_names = { int(h): n for h,n in header_names }
            line_objects = []
            with (sys.stdin if args.filename == '-' else open(args.filename)) as input_file:
                for index, orig_line in enumerate(input_file):
                    orig_line = orig_line.rstrip('\n').split('\t')
                    line = orig_line[0] if args.field < 0 else orig_line[args.field]
                    if index and not index % 10000:
                        print "Read %d lines of input" % (index,)
                    if index == 0:
                        headers = [ '<expanded>' if i == args.field else '' for i in range(len(orig_line)) ]
                        line_objects = [ {} for _ in xrange(len(headers)) ]
                    try:
                        parsed = json.loads(line).iteritems() # pylint: disable=E1101
                    except (ValueError,AttributeError):
                        if index == 0:
                            print "Found header line"
                            headers = [ '<expanded>' if i == args.field else v for i,v in enumerate(orig_line) ]
                            headers = orig_line
                            continue
                        else:
                            raise
                    for k,v in parsed:
                        update(scheme_object, k, v)
                    for i,(e,v) in enumerate(zip(line_objects, orig_line)):
                        try:
                            v = float(v)
                        except ValueError:
                            pass
                        if i != args.field:
                            update(e, 'k', v)
            clear_values(scheme_object)
            for l in line_objects:
                clear_values(l)
            if args.field >= 0:
                scheme_object['#headers'] = [ ('' if args.field == i else o) + (header_names.get(i) or h) 
                                              for i,(h,o) in enumerate(zip(headers, ( orange_tag(e.get('k','')) for e in line_objects ))) ]
                scheme_object['#field'] = args.field
            json.dump(scheme_object, scheme_file) # pylint: disable=E1101

    def print_scheme():
        with open(args.scheme_file) as scheme_file:
            scheme_object = json.load(scheme_file)
            field = scheme_object.pop('#field', -1)
            if field >= 0:
                print 'Field: ', field
                headers = scheme_object.pop('#headers')
                print 'Other headers: ', ', '.join(headers)
            print 'Expanded headers: ', ', '.join(Scheme(scheme_object).get_headers())

    def convert_file():
        with (args.output_file or sys.stdout) as output:
            with (sys.stdin if args.filename == '-' else open(args.filename)) as input_file:
                scheme = None
                headers = []
                header_names = ( hn.split('=') for hn in args.header_name or () )
                header_names = { int(h): n for h,n in header_names }
                field = args.field
                for index, orig_line in enumerate(input_file):
                    orig_line = orig_line.rstrip('\n').split('\t')
                    line = orig_line[0] if args.field < 0 else orig_line[args.field]
                    if index and not index % 10000:
                        print >> sys.stderr, "Read %d lines of input" % (index,)
                    try:
                        parsed = json.loads(line) # pylint: disable=E1101
                        _ = parsed.iteritems
                    except (ValueError,AttributeError):
                        if index == 0:
                            headers = [ orange_tag(h) + h for h in orig_line ]
                            continue
                        else:
                            raise
                    if scheme is None:
                        if args.scheme_file:
                            with open(args.scheme_file) as scheme_file:
                                s_line = next(iter(scheme_file)).strip()
                        else:
                            s_line = line
                        scheme_object = json.loads(s_line) # pylint: disable=E1101
                        field = scheme_object.pop('#field', args.field)
                        assert args.field in (-1, field), 'Field given as argument (%d) does not match field stored in scheme file (%d)' % (args.field, field)
                        headers = scheme_object.pop('#headers', headers)
                        headers = [ header_names.get(i) or h for i,h in enumerate(headers) ]
                        scheme = Scheme(scheme_object)
                        if not args.no_header:
                            if field < 0:
                                output.write(u'\t'.join(scheme.get_headers()).encode('utf-8') + '\n')
                            else:
                                output.write(u'\t'.join(chain(headers[:field], scheme.get_headers(), headers[field+1:])).encode('utf-8') + '\n')
                    if field < 0:
                        output.write(u'\t'.join( unicode(v) for v in scheme(parsed) ).encode('utf-8') + '\n')
                    else:
                        output.write(u'\t'.join(chain(orig_line[:field], ( unicode(v) for v in scheme(parsed) ), orig_line[field+1:])).encode('utf-8') + '\n')
    
    if args.infer_scheme:
        infer_scheme()
    elif args.print_scheme:
        print_scheme()
    else:
        convert_file()
