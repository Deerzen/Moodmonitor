"""Multiprocessing and Itertools are both used to connect to multiple channels.
Classifier is the module that is being called."""

import time
import multiprocessing
from itertools import repeat
import classifier
import scraper


def clamp(n, smallest, largest):
    """Limits n to the range from smallest to largest"""

    return max(smallest, min(n, largest))


def run_pool(method, selection):
    print("Looking up current top channels...")
    channels = scraper.format_top_channels(scraper.find_top_channels())[:selection]

    with multiprocessing.Pool() as pool:
        pool.starmap(classifier.attempt_connection, zip(channels, repeat(method)))

    pool.close()
    pool.terminate()
    pool.join()


def connect(method):
    """Calls the classifier module for every specified channel
    and initiates a connection"""

    selection = clamp(
        int(input("How many channels do you want to connect to (30 max): ")), 1, 30
    )

    while True:
        process = multiprocessing.Process(target=run_pool, args=[method, selection])
        process.start()
        time.sleep(1800)
        process.terminate()
        process.join()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    connect(
        str(input("Which save method do you want to use [local/database]: ")).lower()
    )
