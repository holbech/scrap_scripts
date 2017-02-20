import gzip
from itertools import (chain,
                       groupby,
                       permutations,
                       product)
from operator import attrgetter
import os
import sys

try:
    output_dir = sys.argv[2]
except IndexError:
    output_dir = os.path.abspath(os.curdir)
    
class Mapping():
    __slots__ = tuple('date mjnctids identifiers ie_customercode ie_posix_time ie_age ie_user_agent fe_customercode fe_user_agent ip specificity_level closer_links'.split())
    def __init__(self, *args):
        for k,a in zip(Mapping.__slots__, args):
            if k in ('mjnctids', 'identifiers'):
                a = tuple(a.split('#'))
            if k in ('ie_posix_time', 'ie_age'):
                a = float(a)
            setattr(self, k, a)

def all_match(spec_level):
    return spec_level == 'BrowserAndOSAndCustomerCodeMatch'
all_match.generalizes = ()
all_match.short_name = "F"
def browser_match(spec_level):
    return spec_level in ('BrowserAndOSAndCustomerCodeMatch', 'BrowserAndOSMatch')
browser_match.generalizes = (all_match,)
browser_match.short_name = "B"
def customer_and_os_match(spec_level):
    return spec_level in ('BrowserAndOSAndCustomerCodeMatch', 'OSAndCustomerCodeMatch')
customer_and_os_match.generalizes = (all_match,)
customer_and_os_match.short_name = "U"
def os_match(spec_level):
    return spec_level in ('BrowserAndOSAndCustomerCodeMatch', 'BrowserAndOSMatch', 'OSAndCustomerCodeMatch', 'OSMatch')
os_match.generalizes = (all_match, browser_match, customer_and_os_match)
os_match.short_name = "O"
def customer_match(spec_level):
    return spec_level in ('BrowserAndOSAndCustomerCodeMatch', 'OSAndCustomerCodeMatch', 'CustomerCodeMatch')
customer_match.generalizes = (all_match, customer_and_os_match)
customer_match.short_name = "C"
def no_match(spec_level):
    return True
no_match.generalizes = (all_match, browser_match, customer_and_os_match, os_match, customer_match)
no_match.short_name = "A"
    
def is_legal_algs(algs):
    if len(algs) == 1:
        return True
    for a1 in range(len(algs) - 1):
        for a2 in algs[a1+1:]:
            if a2 in algs[a1].generalizes:
                return False
    return True
    
def create_file(events, algs):
    name = ''.join( a.short_name for a in algs ) + '_' + str(events)
    return open(os.path.join(output_dir, 'mappings.' + name + '.tsv'), 'w')
    
MAX_EVENTS = [ i + 1 for i in range(9) ]
MAX_EVENTS = [1]
BASE_ALGS = (all_match, browser_match, customer_and_os_match, os_match, customer_match, no_match)
PREFERENCES = tuple( algs 
                     for algs in chain.from_iterable( permutations(BASE_ALGS, l + 1) for l in range(len(BASE_ALGS)) )
                     if is_legal_algs(algs) )
ALGORITHMS = list(product(MAX_EVENTS, PREFERENCES))

result_files = { a: create_file(*a)
                 for a in ALGORITHMS }
                  
with gzip.open(sys.argv[1]) as input_file:
    lines = ( l.split('\t') for l in input_file )
    lines = ( Mapping(*l) for l in lines if l )
    current_ip = None
    ip_count = 0
    blanks = " "*30
    for (ip, mjnctids, ie_posix_time), mappings in groupby(lines, key=attrgetter('ip', 'mjnctids', 'ie_posix_time')):
        if ip != current_ip:
            current_ip = ip
            ip_count += 1
            sys.stdout.write("\rMapping on %d (%s) %s" % (ip_count, current_ip, blanks))
        mappings = sorted(mappings, key=attrgetter('ie_age', 'closer_links'))
        mappings = { a: tuple( m for m in mappings if a(m.specificity_level) ) 
                     for a in BASE_ALGS }
        for algs in PREFERENCES:
            try:
                res = next( m for m in ( mappings[a] for a in algs ) if m )
            except StopIteration:
                pass
            else:
                for me in MAX_EVENTS:
                    result_files[(me, algs)].writelines( mi + '\t' + ci + '\n' for e in res[:me] 
                                                                               for mi in e.mjnctids
                                                                               for ci in e.identifiers )
                
for f in result_files.itervalues():
    f.close()
