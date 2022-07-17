"""Socket is needed for connection to twitch chat, traceback for debugging,
warnings turns off unwanted runtime warnings, re is used to format the irc messages,
scraper/predictor/data_processor are modules to improve readability and convenience."""

import os
import socket
import warnings
import traceback
import re
import scraper
import predictor
import data_processor

# Loading the required config data to connect to twitch chat. This must
# have been setup by running the moodmonitor.py script before the needed information
# can be loaded in this script.
CONFIG_DATA = data_processor.read_json("../JSON-Files/config.json")
DIMENSIONS = ["pleasentness", "attention", "sensitivity", "aptitude"]
EVALUATIONS_FOR_REGRESSION = 20


def emote_finder(message, scraped_emotes, emote_data) -> list:
    """Identifies all known emotes in a message and returns them in an array.
    For identification it relies on the scraped emote data."""

    message_list = [message][0].split()
    emote_list = []

    for emote in scraped_emotes:
        for word in message_list:
            if emote == word and emote in emote_data and emote not in emote_list:
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


def archive_prediction(emote, prediction, prediction_data) -> list:
    """Formats the collected prediction data for a particular emote in a message
    and returns a dictionary object that will be added to the prediction_data list."""

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


def handle_predictions(prediction, emote_array, emote_data, prediction_data) -> list:
    """For every emote in a message it passes available prediction data
    to the archive_prediction function. Also it creates average values for all dimensions
    based on the emote_data dictionary. It returns the mutated prediction_data and
    the calculated average values"""

    value_list = []
    for emote in emote_array:
        emote_dict_entry = emote_data[emote]
        if prediction != [0, 0, 0, 0]:
            prediction_data = archive_prediction(emote, prediction, prediction_data)
            print(f"Emote: {emote}")
            print(f"Prediction: {prediction}")

        emote_values = [
            emote_dict_entry["pleasentness"] / emote_dict_entry["times tested"][0],
            emote_dict_entry["attention"] / emote_dict_entry["times tested"][1],
            emote_dict_entry["sensitivity"] / emote_dict_entry["times tested"][2],
            emote_dict_entry["aptitude"] / emote_dict_entry["times tested"][3],
        ]

        # Alters emote_values proportionally so that the most dominant dimension
        # becomes 1 or -1 respectively. This might hurt validity, but it should
        # prevent values from approaching 0 over many repititions and rendering
        # the linear regression useless.
        if max(abs(i) for i in emote_values) != 0:
            multiplicator = 1 / max(abs(i) for i in emote_values)
            for i in range(len(emote_values)):
                emote_values[i] = emote_values[i] * multiplicator

        value_list.append(emote_values)
    return [value_list, prediction_data]


def attempt_connection(channel, method) -> None:
    """Tries to establish a connection to the desired twitch chat. If successful it
    calls the main loop"""

    try:
        server = socket.socket()
        server.connect(("irc.chat.twitch.tv", 6667))
        server.send(bytes("PASS " + CONFIG_DATA[0] + "\r\n", "utf-8"))
        server.send(bytes("NICK " + CONFIG_DATA[1] + "\r\n", "utf-8"))
        server.send(bytes("JOIN " + f"#{channel}" + "\r\n", "utf-8"))
        is_connected = True
        print(f"Successfully connected to {channel}")
        bot_loop(server, is_connected, method, channel)
    # Error message if unsuccessful.
    except ConnectionAbortedError as error:
        error_message = f"Connection to {channel} failed: " + str(error)
        print(error_message)
        traceback.print_exc()


def handle_emote_msg(
    last_evaluations, emote_array, emote_data, prediction_data
) -> list:
    """This function calls other functions to create a prediction, process it
    and to return average values for every dimension that will be used for future
    predictions"""

    prediction = predictor.classify_emotes(
        last_evaluations, EVALUATIONS_FOR_REGRESSION, DIMENSIONS
    )
    result = handle_predictions(prediction, emote_array, emote_data, prediction_data)
    average_values = merge_lists(result[0])

    # returns prediction data and average values for all dimensions
    return [result[1], average_values]


def bot_loop(server, is_connected, method, channel) -> None:
    """Main function which is in a loop as long as the connection to twitch chat
    persists. Every message is decoded & processed in other functions
    based on the contents."""

    # Turning off the occasional run time warning during linear regression
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # Scraping emote data if neccessary
    if not os.path.exists("../JSON-Files/emote-dict.json") or not os.path.exists(
        "../JSON-Files/scraped-emotes.json"
    ):
        scraper.execute()

    # Loading the scraped emote data from stream elements and the json file containing
    # the collected information on emotes. The scraper script must have been
    # executed once before this script can load the required files.
    scraped_emotes = data_processor.read_json("../JSON-Files/scraped-emotes.json")

    if method == "local":
        emote_data = data_processor.read_json("../JSON-Files/emote-dict.json")
    elif method == "database":
        emote_data = data_processor.download_latest_post()

    emote_data = data_processor.evaluate_dict_emotions(emote_data)
    prediction_data = []

    chat_msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    messages_received = 0
    last_evaluations = []

    while is_connected:
        response = server.recv(1024).decode("utf-8", "ignore")
        if "PING" in response:
            server.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            messages_received += 1
            message = chat_msg.sub("", response)
            msg = message.split("\r\n")[0]
            msg = str(msg)
            emote_array = emote_finder(msg, scraped_emotes, emote_data)

            if emote_array:
                emote_result = handle_emote_msg(
                    last_evaluations,
                    emote_array,
                    emote_data,
                    prediction_data,
                )
                prediction_data = emote_result[0]
                last_evaluations.append(emote_result[1])

            if len(last_evaluations) > EVALUATIONS_FOR_REGRESSION:
                last_evaluations.pop(0)

            if messages_received % 500 == 0:
                # if len(prediction_data) < 5:
                #    print(f"Disconnected from {channel} due to lack of data")
                #    is_connected = False
                emote_data = data_processor.save_data(
                    emote_data, prediction_data, method
                )
                prediction_data = []

            elif messages_received % 900 == 0:
                server.send(str.encode("PING tmi.twitch.tv\r\n", "utf-8"))
