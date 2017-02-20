#!/usr/bin/env python

if __name__ == '__main__':
    import sys
    import os
    import string
    import random
    import gzip
    files_count = int(sys.argv[1])
    data_count = int(sys.argv[2])
    output_folder = sys.argv[3]
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    f1s = [ ''.join( random.choice(string.ascii_uppercase) for _ in xrange(5) ) for c in xrange(1000) ]
    f2s = [ ''.join( random.choice(string.ascii_lowercase) for _ in xrange(10) ) for c in xrange(100000) ]
    for i in xrange(files_count):
        i = i + 1
        filename = os.path.join(output_folder,str(i) + '.gz')
        print 'Creating', filename
        with gzip.GzipFile(filename, 'w') as output:
            for j in xrange(data_count):
                f1 = random.choice(f1s)
                f2 = random.choice(f2s)
                f3 = str(random.randint(0,100))
                id = str(i)
                output.write('\t'.join((f1,f2,f3,id)) + '\n')
    
        