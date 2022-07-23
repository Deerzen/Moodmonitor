"""Multiprocessing and Itertools are both used to connect to multiple channels.
Classifier is the module that is being called."""

import os
import time
from multiprocessing import freeze_support
from multiprocessing import Pool
from itertools import repeat
import classifier
import scraper


def clamp(n, smallest, largest):
    """Limits n to the range from smallest to largest"""

    return max(smallest, min(n, largest))


def run_pool(method, selection):

    print("Looking up current top channels...")
    # channels = scraper.format_top_channels(scraper.find_top_channels())[:selection]
    channels = ["xqc", "forsen", "sodapoppin", "hasanabi"]

    pool = Pool(processes=selection)
    pool.starmap_async(classifier.attempt_connection, zip(channels, repeat(method)))

    time.sleep(1800)
    pool.close()
    pool.terminate()
    pool.join()
    print("pool terminated")


def connect(method):
    """Calls the classifier module for every specified channel
    and initiates a connection"""

    while True:
        try:
            run_pool(method, max(os.cpu_count() // 2, 1))
            time.sleep(30)
        except:
            print("error")


if __name__ == "__main__":
    freeze_support()
    connect(
        str(input("Which save method do you want to use [local/database]: ")).lower()
    )
