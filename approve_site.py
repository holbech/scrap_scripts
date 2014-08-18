#!/usr/bin/env python

if __name__ == "__main__":
    import json
    import urllib2
    import sys
    site = sys.argv[1]
    print "Getting status of " + site
    read_request = urllib2.Request('http://bredgade.prod.mojn.com:6000/settings/%s/SiteStatus' % (site,), headers={'Accept': 'application/json'})
    status = json.load(urllib2.urlopen(read_request))
    if not bool(status.get('approved')):
        status['approved'] = True
        print "Approving " + site
        write_request = urllib2.Request('http://bredgade.prod.mojn.com:6000/settings/%s/SiteStatus' % (site,), headers={'Content-Type': 'application/json'}, data=json.dumps(status))
        status = urllib2.urlopen(write_request)
        print "Approved " + site
    