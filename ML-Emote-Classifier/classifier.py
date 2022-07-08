import json
import socket
import pandas as pd
import traceback
import warnings
import statsmodels.api as sm
import re
import scraper

# Turning off the occasional run time warning during linear regression
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Scraping new emotes
print("")
scraper.execute()

# Loading the scraped emote data from stream elements and the json file containing
# the collected information on emotes. The scraper script must have been
# executed once before this script can load the required files.
with open("scraped-emotes.json", "r") as scrape_file:
    scraped_emotes = json.loads(scrape_file.read())
with open("emote-dict.json", "r") as emote_file:
    emote_data = json.loads(emote_file.read())
starting_point = emote_data

# This table enables the script later to identify the most likely emotion
# based on the collected information on pleasentness, attention, sensitivity
# and aptitude.
emotion_table: list = [
    ["optimism", "frivolity", "love", "gloat"],
    ["frustation", "disapproval", "envy", "remorse"],
    ["aggressiveness", "rejection", "rivalry", "contempt"],
    ["anxiety", "awe", "submission", "coercion"],
]

# Loading the required config data to connect to twitch chat. This must
# have been setup by running the moodmonitor.py script before the needed information
# can be loaded in this script.
config_path: str = "../JSON-Files/config.json"
with open(config_path, "r") as config_file:
    config_data = json.loads(config_file.read())


# Identifies all known emotes in a message and returns them in an array.
# For identification it relies on the scraped emote data.
def emote_finder(message) -> list:
    global scraped_emotes
    message_list = [message][0].split()
    emote_list = []

    for emote in scraped_emotes:
        for word in message_list:
            if emote == word and emote not in emote_list:
                emote_list.append(emote)

    return emote_list


# Takes a list with pleasentness, attention, sensitivity and aptitude
# data, calculates the average for each dimenension and returns a merged list.
def merge_lists(lists) -> list:
    merged_list = [0, 0, 0, 0]

    for array in lists:
        for i in range(len(array)):
            merged_list[i] += array[i]

    for i in range(len(merged_list)):
        merged_list[i] = merged_list[i] / len(lists)

    return merged_list


# Simply takes two variables and the length of the evaluations list and calculates
# with a linear regression what the next value will most likely be. In case the
# calculated coefficients are statistically significant it returns the prediction.
# If they are not, a 0 is being returned.
def linear_regression(x, y, evaluations_length) -> float:
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    coef = model.summary2().tables[1]["Coef."]
    prediction = round(coef[0] + coef[1] * (evaluations_length + 1), 2)
    if (
        model.summary2().tables[1]["P>|t|"][0] < 0.05
        and model.summary2().tables[1]["P>|t|"][1] < 0.05
    ):
        return prediction
    else:
        return 0


# Classifies the identified emotes using the four dimensions
# pleasentness, attention, sensitivity and aptitude and returns the predicted
# float values for all four dimensions in an array.
def classify_emotes(emote_array, last_evaluations, needed_evaluations) -> list:
    global emote_data
    dimensions = ["pleasentness", "attention", "sensitivity", "aptitude"]
    formated_evaluations = {"pl": [], "at": [], "se": [], "ap": []}

    # Essentially adds the index numbers of the last evaluations to an array
    # and the values to the respective key in the formated_evaluations dictionary.
    evaluation_numbers = []
    for i in range(len(last_evaluations)):
        evaluation_numbers.append(i)
    for evaluation in last_evaluations:
        formated_evaluations["pl"].append(evaluation[0])
        formated_evaluations["at"].append(evaluation[1])
        formated_evaluations["se"].append(evaluation[2])
        formated_evaluations["ap"].append(evaluation[3])

    # The formatted data can now be transformed in a pandas dataframe for the
    # linear regression.
    df = pd.DataFrame(
        {
            "numbers": evaluation_numbers,
            dimensions[0]: formated_evaluations["pl"],
            dimensions[1]: formated_evaluations["at"],
            dimensions[2]: formated_evaluations["se"],
            dimensions[3]: formated_evaluations["ap"],
        }
    )

    # Checks if the record of evaluations has enough data for linear regression.
    # If it does a linear regression is performed for every emotion dimension.
    # The outcomes are saved in the prediction variable.
    prediction = [0, 0, 0, 0]
    if len(last_evaluations) >= needed_evaluations:
        current_dimension = 0
        x = df[["numbers"]]
        for dimension in dimensions:
            y = df[dimension]
            dimension_prediction = linear_regression(x, y, len(last_evaluations))
            prediction[current_dimension] = dimension_prediction
            current_dimension += 1

    value_list = []
    for emote in emote_array:
        emote_dict_entry = emote_data[emote]

        if prediction != [0, 0, 0, 0]:
            index = 0
            for dimension in dimensions:
                emote_dict_entry[dimension] = round(
                    emote_dict_entry[dimension] + prediction[index], 2
                )
                if prediction[index] != 0:
                    emote_dict_entry["times tested"][index] += 1
                index += 1

            print(f"Emote: {emote}")
            print(f"Prediction: {prediction}")
            emote_dict_entry["likely emotion"] = identify_emotion(
                emote_dict_entry, True
            )

        emote_values = [
            emote_dict_entry["pleasentness"] / emote_dict_entry["times tested"][0],
            emote_dict_entry["attention"] / emote_dict_entry["times tested"][1],
            emote_dict_entry["sensitivity"] / emote_dict_entry["times tested"][2],
            emote_dict_entry["aptitude"] / emote_dict_entry["times tested"][3],
        ]
        value_list.append(emote_values)

    average_values = merge_lists(value_list)
    return average_values


def identify_emotion(emote, is_printing) -> str:
    global emotion_table
    values = [
        emote["pleasentness"],
        emote["attention"],
        emote["sensitivity"],
        emote["aptitude"],
    ]
    hierarchy = [0, 0, 0, 0]
    for i in range(len(values)):
        if values[i] < 0:
            hierarchy[i] = values[i] * -1
        else:
            hierarchy[i] = values[i]
    evaluation = [
        round(emote["pleasentness"] / emote["times tested"][0], 2),
        round(emote["attention"] / emote["times tested"][1], 2),
        round(emote["sensitivity"] / emote["times tested"][2], 2),
        round(emote["aptitude"] / emote["times tested"][3], 2),
    ]
    if is_printing:
        print(f"Times tested: {emote['times tested']}")
        print(
            f"Pl: {evaluation[0]}, At: {evaluation[1]}, Se: {evaluation[2]}, Ap: {evaluation[3]}"
        )

    key: list = [0, 0]
    if hierarchy[0] > hierarchy[2]:
        # pleasentness + attention are dominant
        if hierarchy[1] > hierarchy[3]:
            key = find_data_keys([0, 1], values)
        # pleasentness + aptitude are dominant
        else:
            key = find_data_keys([0, 3], values)
    else:
        # sensitivity + attention are dominant
        if hierarchy[1] > hierarchy[3]:
            key = find_data_keys([2, 1], values)
        # sensitivity + aptitude are dominant
        else:
            key = find_data_keys([2, 3], values)

    if is_printing:
        print(f"Likely emotion: {emotion_table[key[0]][key[1]]}")
        print("")
    return emotion_table[key[0]][key[1]]


# This function identifies the right keys to find the dominant emotion in the emotion_table
def find_data_keys(pair, values) -> list:
    data_keys = [0, 0]
    # if pleasentness is more dominant than sensitivity
    if pair[0] == 0:
        data_keys[0] = return_key(1, values[pair[0]])
    # if sensitivity is more dominant than pleasentness
    elif pair[0] == 2:
        data_keys[0] = return_key(2, values[pair[0]])
    # if attention is more dominant than aptitude
    if pair[1] == 1:
        data_keys[1] = return_key(1, values[pair[1]])
    # if aptitude is more dominant than attention
    elif pair[1] == 3:
        data_keys[1] = return_key(2, values[pair[1]])
    return data_keys


# checks for negative or positive values for one of two possible combinations and returns the appropriate key
def return_key(combination, value) -> int:
    return_values = {1: [1, 0], 2: [3, 2]}

    if value < 0:
        return return_values[combination][0]
    else:
        return return_values[combination][1]


def evaluate_dict_emotions():
    with open("emote-dict.json", "r") as emote_file:
        current_data = json.loads(emote_file.read())

    for emote in current_data:
        current_data[emote]["likely emotion"] = identify_emotion(
            current_data[emote], False
        )

    with open("emote-dict.json", "w") as emote_file:
        json.dump(current_data, emote_file)


def save_data():
    global emote_data
    global starting_point
    current_data = emote_data

    with open("emote-dict.json", "w") as emote_file:
        json.dump(current_data, emote_file)
        print("------ DATA SAVED ------")
        print("")

    evaluate_dict_emotions()

    with open("emote-dict.json", "r") as emote_file:
        emote_data = json.loads(emote_file.read())
        starting_point = emote_data


def attempt_connection() -> None:
    global config_data
    channel = str(input("Channel to connect to: ")).lower()
    print("")
    try:
        server = socket.socket()
        server.connect(("irc.chat.twitch.tv", 6667))
        server.send(bytes("PASS " + config_data[0] + "\r\n", "utf-8"))
        server.send(bytes("NICK " + config_data[1] + "\r\n", "utf-8"))
        server.send(bytes("JOIN " + f"#{channel}" + "\r\n", "utf-8"))
        is_connected = True
        bot_loop(server, is_connected)
    # Error message if unsuccessful.
    except Exception as e:
        error_message = f"Connection to {channel} failed: " + str(e)
        print(error_message)
        traceback.print_exc()


def bot_loop(server, is_connected) -> None:
    global emote_data
    chat_msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    max_evaluations = 40
    messages_received = 0
    last_evaluations = [
        [0, 0, 0, 0],
    ]
    evaluate_dict_emotions()
    while is_connected:
        response = server.recv(1024).decode("utf-8", "ignore")
        if "PING" in response:
            server.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            messages_received += 1
            message = chat_msg.sub("", response)
            msg = message.split("\r\n")[0]
            msg = str(msg)

            emote_array = emote_finder(msg)
            if emote_array != []:
                classification = classify_emotes(
                    emote_array, last_evaluations, max_evaluations
                )
                last_evaluations.append(classification)
            if len(last_evaluations) > max_evaluations:
                last_evaluations.pop(0)
            if messages_received % 500 == 0:
                save_data()
            elif messages_received % 900 == 0:
                server.send(str.encode("PING tmi.twitch.tv\r\n", "utf-8"))


if __name__ == "__main__":
    attempt_connection()
