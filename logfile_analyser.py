#!/usr/bin/env python

if __name__ == "__main__":
    import datetime
    import fnmatch
    import sys
    line_selector = sys.argv[1]
    output_all = len(sys.argv) > 2 and bool(sys.argv[2])
    total = 0.0
    count = 0
    mx_line = ''
    mx = 0.0
    prev_dt = None
    for line in sys.stdin:
        dt = datetime.datetime.strptime(line.split('\t')[0], '%Y-%m-%d %H:%M:%S,%f')
        if fnmatch.fnmatch(line, line_selector):
            time_taken = (dt-prev_dt).seconds + ((dt-prev_dt).microseconds/1000000.0)
            if output_all:
                print str(time_taken) + '\t' + line.rstrip('\n')
            total += time_taken
            count += 1
            if time_taken > mx:
                mx_line = line.rstrip('\n')
                mx = time_taken
        prev_dt = dt
    if not output_all:
        print "Total: " + str(total)
        print "Avg: " + str(total/count)
        print "Max: " + str(mx)
        print "Max-line: " + mx_line

        