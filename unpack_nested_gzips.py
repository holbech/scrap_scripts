#!/usr/bin/env python

if __name__ == "__main__":
    import sys
    import os
    import gzip
    import shutil
    in_dirs = sys.argv[1].split(',')
    head_out_dir = sys.argv[2]
    customer = (sys.argv + [''])[3]
    for in_dir in in_dirs:
        out_dir = os.path.join(head_out_dir, os.path.basename(in_dir))
        print "Unpacking from " + in_dir + " to " + out_dir
        for dirpath, _, filenames in os.walk(in_dir):
            print "Examining", dirpath, '...',
            gzip_files = [ fn for fn in filenames if fn.endswith('.gz') ]
            if gzip_files:
                target_file = dirpath[len(in_dir):].replace(os.path.sep, "_").strip('_')
                if target_file:
                    if not os.path.isdir(out_dir):
                        os.makedirs(out_dir)
                    print "writing to " + os.path.join(out_dir, target_file)
                    with open(os.path.join(out_dir, target_file), 'w') as output_file:
                        for filename in gzip_files:
                            print "Extracting " + filename
                            with gzip.GzipFile(os.path.join(dirpath, filename), 'r') as input_file:
                                if customer:
                                    output_file.writelines( l for l in input_file if customer in l.strip().split('\t') )
                                else:
                                    shutil.copyfileobj(input_file, output_file)
            else:
                print "skipping"
        