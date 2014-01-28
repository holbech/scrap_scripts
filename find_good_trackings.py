

if __name__ == '__main__':
    from collections import defaultdict
    import sys
    def do_print(cookie_id, url_collection):
        print '%05d\t%05d\t%05d\t%s' % (len(url_collection), 
                                        max( len(us) for us in url_collection.itervalues() ), 
                                        min( len(us) for us in url_collection.itervalues() ),
                                        cookie_id)
    current_cookie = None
    urls = defaultdict(set)
    for line in sys.stdin.readlines():
        customer, url, cookie = line.strip().split('\t')[0:3]
        current_cookie = current_cookie or cookie
        if cookie != current_cookie:
            do_print(current_cookie, urls)
            urls = defaultdict(set)
            current_cookie = cookie
        urls[customer].add(url)
    if current_cookie:
        do_print(current_cookie, urls)
        