import json
import socket
import warnings
import traceback
import re
import scraper
import interpreter
import predictor

# Turning off the occasional run time warning during linear regression
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Scraping new emotes
print("")
# scraper.execute()

# Loading the required config data to connect to twitch chat. This must
# have been setup by running the moodmonitor.py script before the needed information
# can be loaded in this script.
config_path: str = "../JSON-Files/config.json"
with open(config_path, "r", encoding="utf8") as config_file:
    CONFIG_DATA = json.loads(config_file.read())
DIMENSIONS = ["pleasentness", "attention", "sensitivity", "aptitude"]


def emote_finder(message, scraped_emotes) -> list:
    """Identifies all known emotes in a message and returns them in an array.
    For identification it relies on the scraped emote data."""

    message_list = [message][0].split()
    emote_list = []

    for emote in scraped_emotes:
        for word in message_list:
            if emote == word and emote not in emote_list:
                emote_list.append(emote)

    return emote_list


def merge_lists(lists) -> list:
    """Takes a list with pleasentness, attention, sensitivity and aptitude
    data, calculates the average for each dimenension and returns a merged list."""

    merged_list = [0, 0, 0, 0]

    for array in lists:
        for i in range(len(array)):
            merged_list[i] += array[i]

    for i in range(len(merged_list)):
        merged_list[i] = merged_list[i] / len(lists)

    return merged_list


def save_prediction(emote, prediction, prediction_data) -> list:
    print("saved")
    collected_data: list = prediction_data

    result: dict = {
        "emote": "",
        "times tested": [0, 0, 0, 0],
        "pleasentness": 0,
        "attention": 0,
        "sensitivity": 0,
        "aptitude": 0,
    }
    result["emote"] = emote

    index = 0
    for dimension in DIMENSIONS:
        result[dimension] = round(prediction[index], 2)
        if prediction[index] != 0:
            result["times tested"][index] += 1
        index += 1

    collected_data.append(result)
    return collected_data


def evaluate_dict_emotions(dictionary) -> dict:
    for emote in dictionary:
        dictionary[emote]["likely emotion"] = interpreter.identify_emotion(
            dictionary[emote], False
        )

    return dictionary


def handle_predictions(prediction, emote_array, emote_data, prediction_data) -> list:
    value_list = []
    for emote in emote_array:
        emote_dict_entry = emote_data[emote]
        if prediction != [0, 0, 0, 0]:
            prediction_data = save_prediction(emote, prediction, prediction_data)
            print(f"Emote: {emote}")
            print(f"Prediction: {prediction}")
        emote_values = [
            emote_dict_entry["pleasentness"] / emote_dict_entry["times tested"][0],
            emote_dict_entry["attention"] / emote_dict_entry["times tested"][1],
            emote_dict_entry["sensitivity"] / emote_dict_entry["times tested"][2],
            emote_dict_entry["aptitude"] / emote_dict_entry["times tested"][3],
        ]
        value_list.append(emote_values)
    return [value_list, prediction_data]


def integrate_predictions(emote_data, prediction_data) -> dict:
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

    print(prediction_data)

    with open("emote-dict.json", "r", encoding="utf8") as json_file:
        json_data = json.loads(json_file.read())

    new_dict = integrate_predictions(json_data, prediction_data)
    new_dict = evaluate_dict_emotions(new_dict)

    print(new_dict)
    exit()

    # print("new dict (json data + prediction data):")
    # print(new_dict)
    # print("")

    with open("emote-dict.json", "w", encoding="utf8") as emote_dict:
        json.dump(new_dict, emote_dict)
        print("------ DATA SAVED ------")
        print("")

    with open("emote-dict.json", "r", encoding="utf8") as emote_dict:
        emote_data = json.loads(emote_dict.read())

    return emote_data


def attempt_connection() -> None:
    channel = str(input("Channel to connect to: ")).lower()
    print("")
    try:
        server = socket.socket()
        server.connect(("irc.chat.twitch.tv", 6667))
        server.send(bytes("PASS " + CONFIG_DATA[0] + "\r\n", "utf-8"))
        server.send(bytes("NICK " + CONFIG_DATA[1] + "\r\n", "utf-8"))
        server.send(bytes("JOIN " + f"#{channel}" + "\r\n", "utf-8"))
        is_connected = True
        bot_loop(server, is_connected)
    # Error message if unsuccessful.
    except Exception as e:
        error_message = f"Connection to {channel} failed: " + str(e)
        print(error_message)
        traceback.print_exc()


def bot_loop(server, is_connected) -> None:

    # Loading the scraped emote data from stream elements and the json file containing
    # the collected information on emotes. The scraper script must have been
    # executed once before this script can load the required files.
    with open("scraped-emotes.json", "r", encoding="utf8") as scrape_file:
        scraped_emotes = json.loads(scrape_file.read())
    with open("emote-dict.json", "r", encoding="utf8") as emote_file:
        emote_data = json.loads(emote_file.read())
    emote_data = evaluate_dict_emotions(emote_data)
    prediction_data = []

    chat_msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    max_evaluations = 20
    messages_received = 0
    last_evaluations = [
        [0, 0, 0, 0],
    ]

    while is_connected:
        response = server.recv(1024).decode("utf-8", "ignore")
        if "PING" in response:
            server.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            messages_received += 1
            message = chat_msg.sub("", response)
            msg = message.split("\r\n")[0]
            msg = str(msg)

            emote_array = emote_finder(msg, scraped_emotes)
            if emote_array:
                prediction = predictor.classify_emotes(
                    last_evaluations, max_evaluations, DIMENSIONS
                )
                result = handle_predictions(
                    prediction, emote_array, emote_data, prediction_data
                )
                prediction_data = result[1]
                value_list = result[0]
                average_values = merge_lists(value_list)
                last_evaluations.append(average_values)
            if len(last_evaluations) > max_evaluations:
                last_evaluations.pop(0)
            if messages_received % 500 == 0:
                emote_data = save_data(emote_data, prediction_data)
                prediction_data = []
            elif messages_received % 900 == 0:
                server.send(str.encode("PING tmi.twitch.tv\r\n", "utf-8"))


if __name__ == "__main__":
    attempt_connection()
