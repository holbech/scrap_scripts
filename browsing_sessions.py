#!/usr/bin/env python

import gzip
import logging
from multiprocessing.dummy import Pool
import os
import sys
from threading import Lock


if __name__ == "__main__":
    input_root = sys.argv[1]
    output_root = sys.argv[2]
    
    _ensure_dir_lock = Lock()
    def _ensure_dir(dirname):
        if not os.path.exists(dirname):
            with _ensure_dir_lock:
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
        
    def filter_file(arg):
        try:
            directory, filename = arg
            input_filename = os.path.join(directory, filename)
            if not filename.endswith('.gz'):
                logging.info("Ignoring " + input_filename)
            output_directory = directory.replace(input_root, output_root)
            _ensure_dir(output_directory)
            output_filename = os.path.join(output_directory, filename)
            with gzip.GzipFile(output_filename, 'w') as output_file:
                with gzip.GzipFile(input_filename, 'r') as input_file:
                    for l in input_file:
                        l = l.split('\t')
                        if len(l) > 6:
                            urls = { u for u in l[6].split('/') }
                            if len(urls) > 1:
                                output_file.write('\t'.join(l[2:]))
            logging.debug("Created " + output_filename)
        except Exception:
            logging.exception('Error on ' + str(arg))

    input_files = ( (d,f) for (d,_,fs) in os.walk(input_root) for f in fs )
    for i,_ in enumerate(Pool(20).imap_unordered(filter_file, input_files, 10)):
        sys.stdout.write(str(i) + '\r')
        sys.stdout.flush()
