#!/usr/bin/env python
import os
import sys
import subprocess
import multiprocessing
    
base_cmd = "s3cmd --no-progress sync %s %s"



def get_content(name, path, out_dir, dates):
    subdirs = ['day', 'midnight'] if name == "sessions" else ['']
    for d in dates:
        for s in subdirs:
            if s:
                d_path = path + s + '/' + d
                out_path = out_dir + "/" + name + '/' + s
            else:
                d_path = path + d
                out_path = out_dir + "/" + name
            if not os.path.isdir(out_path):
                os.makedirs(out_path)
            print "Getting " + d_path + " to " + out_path
            try:
                result = subprocess.check_output(base_cmd % (d_path, out_path + "/"), shell=True)
                print "Downloaded " + str(len([ l for l in result.splitlines() if 'stored as' in l ])) + " from " + name + "/" + s
            except BaseException as ex:
                print "Error downloading " + name + "/" + s + ": " + (getattr(ex, 'message', '') or str(ex))
                raise

if __name__ == '__main__':
    in_bucket = sys.argv[1]
    out_dir = sys.argv[2]
    dates = sys.argv[3:]
    bucket_content = subprocess.check_output("s3cmd ls s3://" + in_bucket, shell=True)
    bucket_content = [ f.partition('DIR')[2].strip().rsplit(' ', 1)[-1] for f in bucket_content.splitlines() if f and 'DIR' in f and '-errors' not in f ]
    bucket_content = [ (f.rstrip('/').rsplit('/', 1)[-1], f) for f in bucket_content ]
    print "Found content: " + ','.join( c for (c,_) in bucket_content )
    pool = multiprocessing.Pool(10)
    for c,p in bucket_content:
        pool.apply_async(get_content, args = (c,p,out_dir, dates))
    pool.close()
    pool.join()
    