import time
import json
from pymongo import MongoClient
import data_processor

CONFIG = data_processor.read_json("../JSON-Files/config.json")
USER_NAME: str = CONFIG[0]
PASSWORD: str = CONFIG[1]
CLUSTER_NAME: str = CONFIG[2]
COLLECTION_NAME: str = CONFIG[3]

cluster = MongoClient(
    f"mongodb+srv://{USER_NAME}:{PASSWORD}@cluster0.qf4tn6b.mongodb.net/?retryWrites=true&w=majority"
)
db = cluster[CLUSTER_NAME]
collection = db[COLLECTION_NAME]


def load_json_dict():
    emote_data = data_processor.read_json("../JSON-Files/emote-dict.json")
    return emote_data


def upload(dataset):
    index = collection.count_documents({})
    local_time = time.ctime(time.time())
    post = {"_id": index, "time": local_time, "data": dataset}
    collection.insert_one(post)
    print(f"{local_time}: Data uploaded successfully")


def download_latest_post() -> dict:
    last_index = collection.count_documents({}) - 1
    results = collection.find_one({"_id": last_index})
    print(results["data"])
    return results["data"]


def main_loop():
    last_upload = {}
    while True:
        emote_data = load_json_dict()
        if emote_data != last_upload:
            upload(emote_data)
        time.sleep(1800)


if __name__ == "__main__":
    main_loop()
