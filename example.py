from workorder import Process, Manager
from random import randint

import time
import random

def task_add(a, b):
    #time.sleep(random.randint(1, 1))
    return a+b

def main():
    manager = Manager()
    results = manager.list()

    jobs = []
    for a in range(5):
        for b in range(5):
            jobs.append(
                Process(target=task_add, args=[a, b], manager=results, debug=True)
            )

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

    print(results)

main()