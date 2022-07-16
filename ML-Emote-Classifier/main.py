import time
import multiprocessing
import classifier


def connect(method):
    c1 = multiprocessing.Process(
        name="xqc", target=classifier.attempt_connection, args=("xqc", method)
    )
    c2 = multiprocessing.Process(
        name="forsen", target=classifier.attempt_connection, args=("forsen", method)
    )
    c3 = multiprocessing.Process(
        name="asmongold",
        target=classifier.attempt_connection,
        args=("asmongold", method),
    )
    c4 = multiprocessing.Process(
        name="mizkif", target=classifier.attempt_connection, args=("mizkif", method)
    )
    c5 = multiprocessing.Process(
        name="hasanabi", target=classifier.attempt_connection, args=("hasanabi", method)
    )
    c6 = multiprocessing.Process(
        name="shroud", target=classifier.attempt_connection, args=("shroud", method)
    )
    c7 = multiprocessing.Process(
        name="pokimane", target=classifier.attempt_connection, args=("pokimane", method)
    )
    c8 = multiprocessing.Process(
        name="summit1g", target=classifier.attempt_connection, args=("summit1g", method)
    )
    c9 = multiprocessing.Process(
        name="amouranth",
        target=classifier.attempt_connection,
        args=("amouranth", method),
    )
    c10 = multiprocessing.Process(
        name="loltyler1",
        target=classifier.attempt_connection,
        args=("loltyler1", method),
    )

    c1.start()
    time.sleep(1)
    c2.start()
    time.sleep(1)
    c3.start()
    time.sleep(1)
    c4.start()
    time.sleep(1)
    c5.start()
    time.sleep(1)
    c6.start()
    time.sleep(1)
    c7.start()
    time.sleep(1)
    c8.start()
    time.sleep(1)
    c9.start()
    time.sleep(1)
    c10.start()

    c1.join()
    c2.join()
    c3.join()
    c4.join()
    c5.join()
    c6.join()
    c7.join()
    c8.join()
    c9.join()
    c10.join()


if __name__ == "__main__":
    connect(
        str(input("Which save method do you want to use [local/database]: ")).lower()
    )
