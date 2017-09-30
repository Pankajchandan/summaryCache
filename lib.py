
import mmh3
import os
from bitarray import bitarray
import math
import socket
import sys
import pickle

## method to make a bloom filter , list_param = list of things, 
## size = size of filter, no_of_hashes = no of hashes
def make_filter(list_param, size, no_of_hashes):
    bit_array = bitarray(size)
    bit_array.setall(0)
    hash_num = 41
    print "building own summary..."
    for url in list_param:
        for i in range(int(no_of_hashes)):
            bit = mmh3.hash(url, hash_num+i) % int(size)
            bit_array[bit] = 1
    
    return bit_array

## method to check if thing is present in bloom filter , bit_array = bloom filter, 
## size = size of filter(no of bits), no_of_hashes = no of hashes, url = object to check
def check_filter(bit_array, size, no_of_hashes, url):
    bit_list = []
    hash_num = 41
    for i in range(int(no_of_hashes)):
        bit_list.append(mmh3.hash(url, hash_num+i) % int(size))
    for bit in bit_list:
        if bit_array[bit] == False:
            return False
    return True

## method to iterate check_filter over all the proxies
def check_filter_list(filter_dict, url):
    ## list all the proxies that might have the URl 
    proxy_true_list = []
    if len(filter_dict) is 0:
        print "empty summary cache..."
        return proxy_true_list

    print "checking in summary cache dictionary"
    for key, value in filter_dict.items():
        if check_filter(value[0], value[1], value[2], url):
            print "found a hit in: ",key
            proxy_true_list.append(key)
    return proxy_true_list

##method to calculate size of a bloom filter and no of hashes required given the no of items and FP probability
def size_hash_calc(items,prob):
    size = math.ceil((items * math.log(prob)) / math.log(1.0 / (pow(2.0, math.log(2.0)))))
    hashes = round(math.log(2.0) * size / items)
    print "size and no of hashes calculated"
    return size, hashes

## method to fetch all the proxies avilable 
## returns a list
def fetch_proxy_list():
    file = open("proxy_list.txt", "r")
    proxy_list = [line[:-1] for line in file]
    file.close()
    print "proxy list fetched from proxy_list.txt"
    return proxy_list[:-1]

## send an object to all remote proxies
def send_filter_details(bit_array, size, no_of_hashes):
    ## fetch list of proxies to send
    proxy_list = fetch_proxy_list()
    ## make a list of filter,size,no_of_hashes
    index_list = [bit_array, size, no_of_hashes]
    ## serialize the object into string using pickle
    index_list_srl = pickle.dumps(index_list)
    ## Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ## Connect the socket to the port where the server is listening
    print "sending own summary to all the proxies online"
    for item in proxy_list:
        server_address = (item, 9000)
        print ('connecting to %s port %s' % server_address)
        try:
            sock.connect(server_address)
            sock.sendall(index_list_srl.encode('utf-8'))
            sock.close()
            print "sent own summary to: ",item
        except socket.error:
            print "proxy offline: ",item

