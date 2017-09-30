# summaryCache
Distributed cache with bloom filters as summaries

A Bloom filter is a space-efficient probabilistic data structure, that is used to test whether an element is a member of a set. False positive matches are possible, but false negatives are not – in other words, a query returns either "possibly in set" or "definitely not in set". Elements can be added to the set, but not removed (though this can be addressed with a "counting" filter) the more elements that are added to the set, the larger the probability of false positives.

This is a project where , we take the idea from the paper “ Summary Cache: A Scalable Wide-Area Web Cache Sharing Protocol by Li Fan, Pei Cao, Jussara Almeida, and Andrei Z. Broder” and show how a probabilistic data structure like bloom filter can reduce network bandwidth usage. We set up a “distributed proxy” environment where each proxy will maintain some cache. Each proxy will maintain a summary of all other proxies in the form of bloom filters. 

To show how a bloom filter helps in reducing network usage, We would setup experiment where a local host will query a number of objects to its local proxy. We would take three caches and compare the gathered matrices. Case 1 is where the local proxy relay the request to the default gateway (internet) if there is a miss in the local proxy. Case 2 is where the local proxy queries all other proxies in case of a cache miss. Case 3 is where the local proxy first queries the local summary bloom filters. Then it queries only those proxies which got a hit in the summary bloom filters. In case of a false positive it queries the default gateway. In case of a miss in bloom filter, it queries the internet. 

![ScreenShot](https://github.com/Pankajchandan/summaryCache/blob/master/image.png)
