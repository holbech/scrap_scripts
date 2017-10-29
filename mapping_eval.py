#!/usr/bin/env python
import json
import sys

with open(sys.argv[1]) as infile:
    lines = ( json.loads(l.strip()) for l in infile if l.strip() )
    evals = { l['mappingType']: l for l in lines }
 
mapping_types = sorted(evals)
stats = [ evals[m] for m in mapping_types ]

def get_quantile(fraction, values, total):
    values = sorted(values.iteritems(), key=lambda x: -x[1])
    subtracted = 0
    key = None
    while subtracted/float(total) < 1 - fraction:
        key, v = values.pop()
        subtracted += v
    return key.strip('_')

def write(head, fields):
    print '\t'.join([head] + [ str(f) for f in fields ])
    
write('', mapping_types)
write('Total', [ s['pairs'] for s in stats ])
write('Accuracy', [ s['accuracy'] for s in stats ])
write('Accuracy coverage', [ (s['positives'] + s['negatives'])/float(s['pairs']) for s in stats ])
write('Hashes', [ s['hashes'] for s in stats ])
write('Hashes seen again', [ s['mappedEhashSeenAfter'][1] for s in stats ])
write('Cookies per hashes 90%', [ get_quantile(0.90, s['hashRankCounts'], s['hashes']) for s in stats ])
write('Cookies per hashes 95%', [ get_quantile(0.95, s['hashRankCounts'], s['hashes']) for s in stats ])
write('Cookies per hashes 99%', [ get_quantile(0.99, s['hashRankCounts'], s['hashes']) for s in stats ])
write('Cookies per hashes 99.9%', [ get_quantile(0.999, s['hashRankCounts'], s['hashes']) for s in stats ])
write('Cookies per hashes 99.99%', [ get_quantile(0.9999, s['hashRankCounts'], s['hashes']) for s in stats ])
write('Hash days active last month median', [ get_quantile(0.50, s['mappedEhashActivityLast31Days'], s['hashes']) for s in stats ])
write('Hash days active last month 90%', [ get_quantile(0.90, s['mappedEhashActivityLast31Days'], s['hashes']) for s in stats ])
write('Hash days active last month 95%', [ get_quantile(0.95, s['mappedEhashActivityLast31Days'], s['hashes']) for s in stats ])
write('Hash days active last month 99%', [ get_quantile(0.99, s['mappedEhashActivityLast31Days'], s['hashes']) for s in stats ])
write('Cookies', [ s['cookies'] for s in stats ])
write('Cookies seen again', [ s['mappedCookieSeenAfter'][1] for s in stats ])
write('Cookies with high bids', [ s['mappedCookieHasHighBids'][1] for s in stats ])
write('Cookies with extreme bids', [ s['mappedCookieHasExtremeBids'][1] for s in stats ])
write('Cookies estimated to be commercial', [ s['mappedCookieEstimatedToBeCommercial'][1] for s in stats ])
write('Third party cookies', [ s['mappedCookieIsThirdParty'][1] for s in stats ])
write('Verified commercial cookies', [ s['mappedCookieIsVerified'][1] for s in stats ])
write('Hashes per cookie 90%', [ get_quantile(0.90, s['cookieRankCounts'], s['cookies']) for s in stats ])
write('Hashes per cookie 95%', [ get_quantile(0.95, s['cookieRankCounts'], s['cookies']) for s in stats ])
write('Hashes per cookie 99%', [ get_quantile(0.99, s['cookieRankCounts'], s['cookies']) for s in stats ])
write('Hashes per cookie 99.9%', [ get_quantile(0.999, s['cookieRankCounts'], s['cookies']) for s in stats ])
write('Hashes per cookie 99.99%', [ get_quantile(0.9999, s['cookieRankCounts'], s['cookies']) for s in stats ])
write('Cookie days active last month median', [ get_quantile(0.50, s['mappedCookieActivityLast31Days'], s['cookies']) for s in stats ])
write('Cookie days active last month 90%', [ get_quantile(0.90, s['mappedCookieActivityLast31Days'], s['cookies']) for s in stats ])
write('Cookie days active last month 95%', [ get_quantile(0.95, s['mappedCookieActivityLast31Days'], s['cookies']) for s in stats ])
write('Cookie days active last month 99%', [ get_quantile(0.99, s['mappedCookieActivityLast31Days'], s['cookies']) for s in stats ])
for mt in mapping_types:
    write('Overlap with ' + mt, [ s['pairsOverlaps'].get(mt,0)/float(s['pairs']) if s['mappingType'] != mt else 1 for s in stats ])
for mt in mapping_types:
    write('Overlap with ' + mt + '(cookies)', [ s['cookiesOverlaps'].get(mt,0)/float(s['cookies']) if s['mappingType'] != mt else 1 for s in stats ])
for mt in mapping_types:
    write('Overlap with ' + mt + '(hashes)', [ s['hashesOverlaps'].get(mt,0)/float(s['hashes']) if s['mappingType'] != mt else 1 for s in stats ])
