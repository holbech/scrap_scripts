#!/usr/bin/env python

if __name__ == "__main__":
    import sys
    import os
    in_dir = sys.argv[1]
    key_fields = [ int(i)-1 for i in sys.argv[2].split(',') ]
    change_fields = None if len(sys.argv) < 4 else [ int(i) for i in sys.argv[3].split(',') ]
    seen_values = {}
    for filename in sorted(os.listdir(in_dir)):
        with open(os.path.join(in_dir, filename), 'r') as input_file:
            for line_no, line in enumerate(input_file):
                line = line.split('\t')
                key = tuple( line[i] for i in key_fields if i < len(line) )
                if change_fields:
                    watch_values = tuple( line[i] for i in change_fields if i < len(line) )
                else:
                    watch_values = tuple( l for i,l in enumerate(line) if i not in key_fields )
                position = filename + ('[%d]' % (line_no,))
                if key in seen_values and seen_values[key][1] != watch_values:
                    print "%s changed between %s and %s (from %s to %s)" % (str(key), seen_values[key][0], position, seen_values[key][1], watch_values)
                seen_values[key] = (position, watch_values)
