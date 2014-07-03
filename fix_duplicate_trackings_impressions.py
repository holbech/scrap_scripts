#!/usr/bin/env python

class StatsCollector():
    def __init__(self):
        self.trackings = []
    
    def update(self, trackings):
        self.trackings.extend(trackings)
    
    def get_pt(self):
        return []
    
    def get_us(self):
        return []

def clean_session(session_line):
    if '/' not in session_line:
        return session_line
    line_parts = session_line.split('\t')
    urls, times = [ splits for splits in ( s.split('/') for s in line_parts ) if len(splits) > 1 ][0:2]
    cleaned_urls = []
    cleaned_times = [] 
    for u,t in zip(reversed(urls), reversed(times)):
        if not (t == "0" and [u] == cleaned_urls[-1:]):
            cleaned_urls.append(u)
            cleaned_times.append(t)
    cleaned_urls.reverse()
    cleaned_times.reverse()
    return session_line.replace('/'.join(urls), '/'.join(cleaned_urls)).replace('/'.join(times), '/'.join(cleaned_times))

if __name__ == "__main__":
    import gzip
    import sys
    import os
    for dirpath, _, filenames in os.walk(os.path.join(sys.argv[1], 'trackings')):
        if filenames:
            customer = os.path.basename(dirpath)
            date = os.path.basename(os.path.dirname(dirpath))
            print "Cleaning up trackings of %s/%s" % (date,customer)
            url_stats_collector = StatsCollector()
            for fn in filenames:
                file_name = os.path.join(dirpath, fn)
                with gzip.open(file_name, 'r') as input_file:
                    content = set(input_file)
                content = sorted(content)
                with gzip.open(file_name, 'w') as output_file:
                    output_file.writelines(content)
                url_stats_collector.update(content)
            with gzip.open(os.path.join(dirpath.replace('trackings', 'page-transitions'), customer), 'w') as pt_file:
                pt_file.writelines( '\t'.join(pt) + '\n' for pt in url_stats_collector.get_pt() )
            with gzip.open(os.path.join(dirpath.replace('trackings', 'url-stats'), customer), 'w') as us_file:
                us_file.writelines( '\t'.join(pt) + '\n' for us in url_stats_collector.get_us() )
    for dirpath, _, filenames in os.walk(os.path.join(sys.argv[1], 'impressions')):
        if filenames:
            customer = os.path.basename(dirpath)
            date = os.path.basename(os.path.dirname(dirpath))
            print "Cleaning up impressions of %s/%s" % (date,customer)
            for fn in filenames:
                file_name = os.path.join(dirpath, fn)
                with gzip.open(file_name, 'r') as input_file:
                    content = set(input_file)
                content = sorted(content)
                with gzip.open(file_name, 'w') as output_file:
                    output_file.writelines(content)
    for dirpath, _, filenames in os.walk(os.path.join(sys.argv[1])):
        if filenames and 'session' in dirpath:
            customer = os.path.basename(dirpath)
            date = os.path.basename(os.path.dirname(dirpath))
            session_type = os.path.basename(os.path.dirname(os.path.dirname(dirpath)))
            print "Cleaning up %s of %s/%s" % (session_type, date,customer)
            for fn in filenames:
                file_name = os.path.join(dirpath, fn)
                with gzip.open(file_name, 'r') as input_file:
                    content = [ clean_session(l) for l in input_file ]
                with gzip.open(file_name, 'w') as output_file:
                    output_file.writelines(content)
                