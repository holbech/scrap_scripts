#!/usr/bin/env python

import gzip
import logging
from multiprocessing.dummy import Pool
import os
import shutil
import sys
import tempfile
from threading import Lock


if __name__ == "__main__":
    root = sys.argv[1]
    
    _ensure_dir_lock = Lock()
    def _ensure_dir(dirname):
        if not os.path.exists(dirname):
            with _ensure_dir_lock:
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
        
    def process_file(arg):
        try:
            directory, filename = arg
            is_aug = 'augmented' in directory
            input_filename = os.path.join(directory, filename)
            if not filename.endswith('.gz'):
                logging.info("Ignoring " + input_filename)
                return
            if is_aug:
                other_dir = directory.replace('augmented-', '')
                other_filename = input_filename.replace('augmented-', '')
            else:
                other_dir = directory.replace('sessions-', 'augmented-sessions-')
                other_filename = input_filename.replace('sessions-', 'augmented-sessions-')
            wrongs = False
            with tempfile.NamedTemporaryFile(delete=True) as output_file:
                with gzip.GzipFile(input_filename, 'r') as input_file:
                    with tempfile.NamedTemporaryFile(delete=True) as wrongs_output_file:
                        for l in input_file:
                            line_is_aug = not l.startswith('201')
                            if line_is_aug != is_aug:
                                wrongs = True
                                wrongs_output_file.write(l)
                            else:
                                output_file.write(l)
                        if wrongs:
                            logging.warning("Splitting " + input_filename)
                            if os.path.exists(other_filename):
                                with gzip.GzipFile(other_filename, 'r') as other_file:
                                    shutil.copyfileobj(other_file, wrongs_output_file)
                            _ensure_dir(other_dir)
                            wrongs_output_file.flush()
                            with open(wrongs_output_file.name, 'r') as i:
                                with gzip.GzipFile(other_filename, 'w') as o:
                                    shutil.copyfileobj(i, o)
                if wrongs:
                    output_file.flush()
                    with open(output_file.name, 'r') as i:
                        with gzip.GzipFile(input_filename, 'w') as o:
                            shutil.copyfileobj(i, o)
        except Exception:
            logging.exception('Error on ' + str(arg))

    input_files = ( (d,f) for (d,_,fs) in os.walk(root) for f in fs )
    for i,_ in enumerate(Pool(20).imap_unordered(process_file, input_files, 10)):
        sys.stdout.write(str(i) + '\r')
        sys.stdout.flush()
    input_files = ( (d,f) for (d,_,fs) in os.walk(root.replace('augmented-', '')) for f in fs )
    for i,_ in enumerate(Pool(20).imap_unordered(process_file, input_files, 10)):
        sys.stdout.write(str(i) + '\r')
        sys.stdout.flush()
