"""The JSON module is needed to read from and write to JSON files.
The imported inerpreter module helps to classify all emotions based
on the collected data"""
import json
import interpreter


def read_json(path):
    """Reads json at specified path"""

    with open(path, "r", encoding="utf8") as json_file:
        json_data = json.loads(json_file.read())
    return json_data


def write_json(data, path) -> None:
    """Writes data to json at specified path"""

    with open(path, "w", encoding="utf8") as json_file:
        json.dump(data, json_file)


def evaluate_dict_emotions(dictionary) -> dict:
    """Loops through the dictionary and interprets the data for every emote.
    Based on a table in the interpreter module it assigns the most likely emotion"""

    for emote in dictionary:
        dictionary[emote]["likely emotion"] = interpreter.identify_emotion(
            dictionary[emote], False
        )
    return dictionary


def integrate_predictions(emote_data, prediction_data) -> dict:
    """Simply integrates the collected prediction data in the emote_data dictionary.
    The mutated dictionary is returned by the function"""

    dictionary = emote_data
    data_points = [
        "times tested",
        "pleasentness",
        "attention",
        "sensitivity",
        "aptitude",
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


def save_data(emote_data, prediction_data) -> list:
    """Integrates the collected data in the emote_data and saves it to the json file"""

    path_dict = "../JSON-Files/emote-dict.json"
    json_data = read_json(path_dict)
    new_dict = integrate_predictions(json_data, prediction_data)
    new_dict = evaluate_dict_emotions(new_dict)
    write_json(new_dict, path_dict)

    print("------ DATA SAVED ------")
    print("")

    emote_data = read_json(path_dict)

    return emote_data
