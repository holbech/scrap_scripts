#!/usr/bin/env python

import logging
import re
import subprocess
import threading

logging.getLogger().setLevel(logging.INFO)

day_extracter = re.compile('tracking/(20\d\d\d\d\d\d)/.')

def move_dates(id, dates):
    for day in dates:
        command = 's3cmd mv s3://idtargeting-logs/tracking/%s/* s3://idtargeting-logs/tracking/ymd=%s/' % (day, day)
        try:
            logging.info('%d: Copying %s', id, day)
            subprocess.check_call(command, shell=True)
        except Exception:
            logging.exception('%d: Failed Copying %s', id, day)

if __name__ == '__main__':
    keys = subprocess.check_output('s3cmd ls --recursive s3://idtargeting-logs/tracking/', shell=True)
    days = set()
    for key in keys.splitlines():
        matches = re.findall(day_extracter, key)
        if len(matches) > 1:
            logging.warn("Found more than one match in line: " + key)
        elif len(matches) == 0:
            logging.warn("Found no match in line: " + key)
        else:
            days.add(matches[0])
    days = [ (i%10,d) for i,d in enumerate(sorted(days)) ]
    operations = [ threading.Thread(target=move_dates, args=(i, [ d for (j,d) in days if i==j ],)) for i in xrange(10) ]
    for t in operations:
        t.daemon = True
        t.start()
    for t in operations:
        t.join()
        