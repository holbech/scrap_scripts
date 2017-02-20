import sys

column = int(sys.argv[1]) - 1
output_base = sys.argv[2]
try:
    buckets = int(sys.argv[3])
except IndexError:
    buckets = 10

def create_file(bucket):
    return open(output_base + '_' + str(bucket), 'w')

files = {}
for line in sys.stdin:
    ip_bucket = hash(line.split('\t')[column]) % buckets
    try:
        files[ip_bucket].write(line)
    except KeyError:
        files[ip_bucket] = create_file(ip_bucket)
        files[ip_bucket].write(line)
        
for f in files.itervalues():
    f.close()
