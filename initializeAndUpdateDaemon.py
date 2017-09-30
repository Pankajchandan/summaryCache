from lib import send_filter_details, make_filter, size_hash_calc
import os
import time
import sys

def make_cache_list():
    cache_list = os.listdir('cache')
    return cache_list

def main(update_time, prob):
    while True:
        cache_list = make_cache_list()
        size, hashes = size_hash_calc(len(cache_list), prob)
        print "building filter of size and hashes : ", size, hashes
        own_summary = make_filter(cache_list, int(size), int(hashes))
        send_filter_details(own_summary, size, hashes)
        print "update sent"
        time.sleep(update_time)
        print "\n\n"

if __name__=="__main__":
    try:
        main(int(sys.argv[1]), float(sys.argv[2]))
    except KeyboardInterrupt:
        print "port terminated"
