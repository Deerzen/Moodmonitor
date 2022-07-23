"""The JSON module is needed to read from and write to JSON files.
The imported inerpreter module helps to classify all emotions based
on the collected data"""

import time
import json
from pymongo import MongoClient

with open("../JSON-Files/config.json", "r", encoding="utf8") as config_file:
    CONFIG = json.loads(config_file.read())
USER_NAME: str = CONFIG[2][0]
PASSWORD: str = CONFIG[2][1]
CLUSTER_NAME: str = CONFIG[2][2]
COLLECTION_NAME: str = CONFIG[2][3]

cluster = MongoClient(
    f"mongodb+srv://{USER_NAME}:{PASSWORD}@cluster0.qf4tn6b.mongodb.net/?retryWrites=true&w=majority"
)
db = cluster[CLUSTER_NAME]
collection = db[COLLECTION_NAME]


def read_json(path):
    """Reads json at specified path"""

    with open(path, "r", encoding="utf8") as json_file:
        json_data = json.loads(json_file.read())
    return json_data


def write_json(data, path) -> None:
    """Writes data to json at specified path"""

    with open(path, "w", encoding="utf8") as json_file:
        json.dump(data, json_file)


def load_json_dict():
    emote_data = read_json("../JSON-Files/emote-dict.json")
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
    return results["data"]


def identify_emotion(emote) -> list:
    """Returns the respective emotion for each dimension based on the recorded values."""

    # This table contains the emotions for each dimension going from very positive (1)
    # to very negative (-1).
    emotion_table: list = [
        ["ecstasy", "joy", "contentment", "melancholy", "sadness", "grief"],
        ["bliss", "calmness", "serenity", "annoyance", "anger", "rage"],
        ["enthusiasm", "eagerness", "responsiveness", "anxiety", "fear", "terror"],
        ["delight", "pleasentness", "acceptance", "dislkike", "disgust", "loathing"],
    ]
    emotions = []
    evaluation = [
        round(emote["introspection"] / emote["times tested"][0], 2),
        round(emote["temper"] / emote["times tested"][1], 2),
        round(emote["sensitivity"] / emote["times tested"][2], 2),
        round(emote["attitude"] / emote["times tested"][3], 2),
    ]

    index = 0
    for value in evaluation:
        combinations = {0: 0.66, 1: 0.33, 2: 0, 3: -0.33, 4: -0.66, 5: -2000}
        for key, threshold in combinations.items():
            if value >= threshold:
                emotions.append(emotion_table[index][key])
                index += 1
                break

    return emotions


def evaluate_dict_emotions(dictionary) -> dict:
    """Loops through the dictionary and interprets the data for every emote.
    Based on a table in the interpreter module it assigns the most likely emotion"""

    for emote in dictionary:
        dictionary[emote]["emotions"] = identify_emotion(dictionary[emote])
    return dictionary


def integrate_predictions(emote_data, prediction_data) -> dict:
    """Simply integrates the collected prediction data in the emote_data dictionary.
    The mutated dictionary is returned by the function"""

    dictionary = emote_data
    data_points = [
        "times tested",
        "introspection",
        "temper",
        "sensitivity",
        "attitude",
    ]

    for emote in dictionary:
        for prediction in prediction_data:
            for point in data_points:
                if emote == prediction["emote"]:
                    if point == "times tested":

                        for i in range(len(prediction[point])):
                            dictionary[emote][point][i] = round(
                                dictionary[emote][point][i] + prediction[point][i], 2
                            )

                    else:
                        dictionary[emote][point] = round(
                            dictionary[emote][point] + prediction[point], 2
                        )
    return dictionary


def local_save(emote_data, prediction_data) -> dict:
    """Saving the data locally in a JSON file"""

    path_dict = "../JSON-Files/emote-dict.json"
    json_data = read_json(path_dict)
    new_dict = integrate_predictions(json_data, prediction_data)
    new_dict = evaluate_dict_emotions(new_dict)
    write_json(new_dict, path_dict)

    print("------ DATA SAVED ------")
    print("")

    emote_data = read_json(path_dict)

    return emote_data


def database_save(emote_data, prediction_data) -> dict:
    """saving the database in a mongodb collection"""

    db_data = download_latest_post()
    new_dict = integrate_predictions(db_data, prediction_data)
    new_dict = evaluate_dict_emotions(new_dict)
    upload(new_dict)

    emote_data = download_latest_post()
    return emote_data


def save_data(emote_data, prediction_data, method) -> dict:
    """Integrates the collected data in the emote_data and saves it to the json file"""

    if method == "local":
        return local_save(emote_data, prediction_data)
    elif method == "database":
        return database_save(emote_data, prediction_data)


# upload(read_json("../JSON-Files/emote-dict.json"))
# write_json(download_latest_post(), "../JSON-Files/emote-dict.json")
