from workorder import Process, Manager, NodePool
from random import randint

import math
import time
import random

# define the task to run
# https://projecteuler.net/problem=206
def task_206(from_, length_):
    for n in range(from_, from_ + length_):
        form = "1{}2{}3{}4{}5{}6{}7{}8{}9{}0".format(*[c for c in str(n).zfill(9)])
        if int(math.sqrt(int(form))) ** 2 == int(form):
            return int(math.sqrt(int(form)))
def main():
    # assign the nodes
    pool = NodePool.get_instance()
    pool.add_node('209.97.167.177')
    pool.add_node('68.183.177.168')
    pool.add_node('68.183.179.112')
    pool.add_node('157.230.32.114')
    pool.add_node('157.230.40.150')
    pool.add_node('157.230.36.53')
    pool.add_node('178.128.126.130')
    pool.add_node('157.230.36.176')
    pool.add_node('157.230.36.195')

    # limit the local node
    pool.local_node = 3

    # create manager to collect the result into list
    manager = Manager()
    results = manager.list()

    # run the jobs
    jobs = []

    length_ = 50_000_000
    for i in range(1, 1_000_000_000, length_):
        p = Process(
            target=task_206,
            args=[i, length_],
            manager=results,
            debug=True
        )
        jobs.append(p)
        p.start()

        # this algorithm have to stop if found any result
        if len(results):
            break

    for j in jobs:
        j.join()

    # consume the results
    print(results)

main()
