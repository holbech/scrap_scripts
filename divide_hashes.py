#!/usr/bin/env python

import sys
from math import floor,ceil

def get_prefix(min_percentage, max_percentage, current_prefix='', current_min_percentage=0.0, current_max_percentage=1.0):
    current_range = current_max_percentage-current_min_percentage
    step_length = current_range/16
    slack = ((max_percentage + min_percentage)/2) - current_min_percentage
    closest_digit = int(round(slack/step_length))
    closest_percentage = current_min_percentage + (step_length*closest_digit)
    if min_percentage < closest_percentage < max_percentage:
        return (current_prefix + hex(closest_digit)[-1]).rstrip('0')
    else:
        less_than_digit = int(floor(slack/step_length))
        less_than_percentage = current_min_percentage + (step_length*less_than_digit)
        return get_prefix(min_percentage, 
                          max_percentage, 
                          current_prefix + hex(less_than_digit)[-1], 
                          less_than_percentage, less_than_percentage + step_length)
    
divisions = [ float(v) for v in sys.argv[1:] if v.replace('.','0').isdigit() ]
max_deviation = next( float(e.partition('=')[2]) for e in sys.argv[1:] + ['dmax=0.01'] if e.startswith('dmax=') )

total = sum(divisions)
divisions = [ v/total for v in divisions ]

total = 0.0
for size in divisions:
    print get_prefix(max(0,total-max_deviation), min(1.0,total+max_deviation)) if total else '0'
    total = total + size
    