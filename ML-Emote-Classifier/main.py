"""Multiprocessing and Itertools are both used to connect to multiple channels.
Classifier is the module that is being called."""

from multiprocessing import Pool, freeze_support
from itertools import repeat
import classifier
import scraper


def clamp(n, smallest, largest):
    """Limits n to the range from smallest to largest"""

    return max(smallest, min(n, largest))


def connect(method):
    """Calls the classifier module for every specified channel
    and initiates a connection"""

    selection = clamp(
        int(input("How many channels do you want to connect to (30 max): ")), 1, 30
    )
    print("Looking up current top channels...")
    channels = scraper.format_top_channels(scraper.find_top_channels())[:selection]

    with Pool() as pool:
        pool.starmap(classifier.attempt_connection, zip(channels, repeat(method)))


if __name__ == "__main__":
    freeze_support()
    connect(
        str(input("Which save method do you want to use [local/database]: ")).lower()
    )
