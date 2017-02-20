
# alias sortfast='sort -S$(($(sed '\''/MemF/!d;s/[^0-9]*//g'\'' /proc/meminfo)/2048)) $([ `nproc` -gt 1 ]&&echo -n --parallel=`nproc`)'

# assumes input files are pre-sorted by 
# zcat final-tc/* | sortfast -t$'\001' -k2,2 -k1,1  | gzip > tc.gz

from collections import (defaultdict,
                         namedtuple)
from itertools import groupby
import logging
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s\t%(levelname)s\t%(message)s')

tracking_file = sys.argv[1]
whitelist_file = sys.argv[2]

Tracking = namedtuple('Tracking', 'date customer cookie is_click')
Mapping = namedtuple('Mapping', 'date customer cookie is_mapped')

trackings = ( Tracking(*[ p.strip() for p in l.split(chr(1)) ]) for l in open(tracking_file) )
mappings = ( Mapping(*[ p.strip() for p in l.split(chr(1)) ]) for l in open(whitelist_file) )

trackings = groupby(trackings, lambda r: (r.customer, r.date))
mappings = groupby(mappings, lambda r: (r.customer, r.date))

tr_group, trs = next(trackings)
next_m_group, maps = next(mappings)

logging.debug('Handling trackings of %s / %s', *tr_group)

is_mapped = ()

m_group = next_m_group

with open('/tmp/counts.tsv', 'w') as output:
    while tr_group:
        while next_m_group and next_m_group <= tr_group:
            logging.debug('Using mappings of %s / %s', *next_m_group)
            is_mapped = { m.cookie for m in maps if m.is_mapped == '1' }
            m_group = next_m_group
            try:
                next_m_group, maps = next(mappings)
            except StopIteration:
                next_m_group = None
        if m_group[0] == tr_group[0]:
            counts = defaultdict(set)
            logging.debug('Counting')
            for tracking in trs:
                counts[(tracking.is_click, str(int( tracking.cookie in is_mapped)))].add(tracking.cookie)
            for kind, cookies in counts.iteritems():
                output.write('\t'.join((tr_group[0], tr_group[1], kind[0], kind[1], str(len(cookies)))) + '\n' )
        else:
            sum( 0 for _ in trs  )
        try:
            tr_group, trs = next(trackings)
            logging.debug('Handling trackings of %s / %s', *tr_group)
        except StopIteration:
            tr_group = None
