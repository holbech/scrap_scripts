
good_cookies = """"
00003    00027    00019    250lxyvqpezm6vijde
00003    00121    00012    4a6m4i6j4jnn6q3tfg
00004    00009    00004    5x4d5ki5jdkhhs0bs3
00004    00012    00003    7lgr2x41lua7vbbmv
00004    00015    00003    8cm0t8wd2okott0emi
00004    00015    00005    2hryhfdge2qfhmuyct
00004    00016    00001    6y132aijlai4c15ynq
00004    00016    00001    7rnfuxylc8uln833f0
00004    00016    00004    4ox0koe7bj6mt3zftu
00004    00016    00009    4ijcxqmb8j8jkg0rp0
00004    00048    00015    2gpq9e57tbrabbs1xd
00005    00008    00004    41dd4ql7oegmko7pq7
00005    00040    00001    2g3qzs6ae0krifd1zw
00006    00021    00001    3p2er9u6l60bwe9bfl
"""
good_cookies = [ l.strip().split()[-1] for l in good_cookies.splitlines() if l.split() ]


if __name__ == '__main__':
    import sys
    for line in sys.stdin.readlines():
        _, _, cookie = line.strip().split('\t')[0:3]
        if cookie in good_cookies:
            print line,
    
            
