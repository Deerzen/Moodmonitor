"""Multiprocessing and Itertools are both used to connect to multiple channels.
Classifier is the module that is being called."""

import time
from multiprocessing import Pool
from itertools import repeat
import classifier
import scraper


def clamp(n, smallest, largest):
    """Limits n to the range from smallest to largest"""

    return max(smallest, min(n, largest))


def run_pool(method, selection):

    print("Looking up current top channels...")
    channels = scraper.format_top_channels(scraper.find_top_channels())[:selection]

    pool = Pool(processes=selection)
    pool.starmap_async(classifier.attempt_connection, zip(channels, repeat(method)))

    time.sleep(1800)
    pool.close()
    pool.terminate()
    pool.join()
    print("pool ended")


def connect(method):
    """Calls the classifier module for every specified channel
    and initiates a connection"""

    selection = clamp(
        int(input("How many channels do you want to connect to (30 max): ")), 1, 30
    )

    while True:
        run_pool(method, selection)
        time.sleep(30)


if __name__ == "__main__":
    connect(
        str(input("Which save method do you want to use [local/database]: ")).lower()
    )
