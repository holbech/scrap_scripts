#!/usr/bin/env python

if __name__ == "__main__":
    import sys
    import os
    for dirpath, _, filenames in os.walk(sys.argv[1]):
        for fn in filenames:
            file_name = os.path.join(dirpath, fn)
            print "Sorting " + file_name
            with open(file_name, 'r') as input_file:
                content = list(input_file)
            content.sort()
            with open(file_name, 'w') as output_file:
                output_file.writelines(content)

