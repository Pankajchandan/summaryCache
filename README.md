# summaryCache
Distributed cache with bloom filters as summaries

A Bloom filter is a space-efficient probabilistic data structure, that is used to test whether an element is a member of a set. False positive matches are possible, but false negatives are not – in other words, a query returns either "possibly in set" or "definitely not in set". Elements can be added to the set, but not removed (though this can be addressed with a "counting" filter) the more elements that are added to the set, the larger the probability of false positives.

This is a project where , we take the idea from the paper “ Summary Cache: A Scalable Wide-Area Web Cache Sharing Protocol by Li Fan, Pei Cao, Jussara Almeida, and Andrei Z. Broder” and show how a probabilistic data structure like bloom filter can reduce network bandwidth usage. We set up a “distributed proxy” environment where each proxy will maintain some cache. Each proxy will maintain a summary of all other proxies in the form of bloom filters. 

To show how a bloom filter helps in reducing network usage, We would setup experiment where a local host will query a number of objects to its local proxy. We would take three caches and compare the gathered matrices. Case 1 is where the local proxy relay the request to the default gateway (internet) if there is a miss in the local proxy. Case 2 is where the local proxy queries all other proxies in case of a cache miss. Case 3 is where the local proxy first queries the local summary bloom filters. Then it queries only those proxies which got a hit in the summary bloom filters. In case of a false positive it queries the default gateway. In case of a miss in bloom filter, it queries the internet. 

![ScreenShot](https://github.com/Pankajchandan/summaryCache/blob/master/image.png)


1. Git clone the code on all the proxy server. 
	$ git clone https://github.com/Pankajchandan/summaryCache.git

2. List all the participating host’s ip address in proxy_list.txt including localhost.

3.   Place all the caches in cache folder. Here the folder’s name will be the website’s name 

4.   Run proxy1.py on the main proxy server that is directly connected to client.
            $ python  proxy1.py

5.   Run proxy2.py on all the secondary proxy servers.
            $ python proxy2.py

6.   Run initialize and update daemon script on all the proxy servers.
            $ python initializeAndUpdateDaemon.py [time interval in s] [false positive probability] 
            Ex: $ python initializeAndUpdateDaemon.py 300 0.01

7.   You can test using client.ipynb or any web browser like chrome. Remember to set proxy to proxy1’s ip



####Lib.py has these following utility methods.

1. make_filter(list_param, size, no_of_hashes):

method to make a bloom filter , list_param = list having all the websites’  names, size = size of filter, no_of_hashes = no of hashes to be used

Returns  a bit array (bloom filter)

2. check_filter(bit_array, size, no_of_hashes, url):

method to check if object is present in a single bloom filter , bit_array = bloom filter, size = size of filter(no of bits), no_of_hashes = no of hashes being used in the filter, url = website address

Returns True if present ele false

3. check_filter_list(filter_dict, url):

method to iterate check_filter method over all the bloom filters filter dict = dictionary of bloom filters to check, url = object to check

Returns a list of proxies ip addresses who has the object in their cache

4. size_hash_calc(items,prob):

method to calculate size of a bloom filter and no of hashes required given the no of items and False Positive probability
Returns size and number of hashes to be used to make the bloom filter

5. fetch_proxy_list():
method to fetch all the proxies available

Returns a list of ip addresses

6. send_filter_detail_worker(item,index_list_srl):

Method to send index_list_srl bloom filter to item. Item = ip address of the remote host (proxy)  to which item_list_srl is to be sent.
item_list _srl = serialized item_list
Item_list = a list of localhost’s bloom filter, size of the filter and no of hashes used to make the filter

Returns null

7. send_filter_details(bit_array, size, no_of_hashes):

Method to iterate send_filter_detail_worker over all the remote proxies.
Bit_array = the bloom filter of local host , size = size of the filter, no_of_hashes= no of hashes used to make the filter. Spins a thread for each proxy to which the details is to be sent. Send_filter_details is the callback function for the spawned thread.

Returns null


####initializeAndUpdateDaemon.py 
Builds the localhost bloom filter once on every X seconds and sends it to all other proxies

####Proxy1.py
1. load_backup(filename):
Method to load cache history when server is run

2. RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
Inherited class which handles http requests

3. request_proxy(self, proxy, cache_name):
Is a function in class RequestHandler This method sends request to all other proxies in case of a local cache miss.

4. run_port(sock,filter_dict):
Is a method that runs tcp server on port 9000 on localhost to recieve all the bloom filters from all other proxies. When listens to a connection calls back add_filter on a thread and keeps listening.

5. port_close():
Method to kill thread on which tcp server is running.

6. add_filter(connection, client_address):
Method to add the filter recieved from a proxy to the local filter dictionary.

7. run_servers():
Method to initialize tcp and http server. Calls back run_port on a thread and and runs http server on main process. 


####Proxy2.py
Has all the functionalities of proxy1.py except the request_proxy part.


