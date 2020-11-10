#!/usr/bin/python3
import random, string, subprocess
import time
from multiprocessing.pool import ThreadPool as Pool
import csv
import requests

pool_size = 8


def worker(i):
    try:
        longResource = "http://"+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(100))
        # shortResource = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

        #request="http://127.0.0.1:4000/?short={}&long={}".format(i, longResource)
        
        request="http://127.0.0.1:8000/"
        r = requests.put(request, params={'short':str(i), 'long':longResource})
    except Exception as e:
        print(e)


numWrites = [10, 100, 1000, 4000]

with open('./data/varying_writes.tsv', 'wt') as out_file:

    for i in range (len(numWrites)):

        pool = Pool(pool_size)
        t0 = time.time()

        for j in range(numWrites[i]):
            pool.apply_async(worker, (j,))


        pool.close()
        pool.join()

        t1 = time.time()

        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow([t1-t0, numWrites[i]])
        print("{} writes: {} seconds".format(numWrites[i],t1-t0))
