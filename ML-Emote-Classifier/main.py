"""Multiprocessing and Itertools are both used to connect to multiple channels.
Classifier is the module that is being called."""

from multiprocessing import Pool, freeze_support
from itertools import repeat
import classifier


def connect(method):
    """Calls the classifier module for every specified channel
    and initiates a connection"""

    channels = [
        "xqc",
        "forsen",
        "mizkif",
        "hasanabi",
        "sodapoppin",
        "asmongold",
        "shroud",
        "pokimane",
        "summit1g",
        "loltyler1",
    ]

    with Pool() as pool:
        pool.starmap(classifier.attempt_connection, zip(channels, repeat(method)))


if __name__ == "__main__":
    freeze_support()
    connect(
        str(input("Which save method do you want to use [local/database]: ")).lower()
    )
