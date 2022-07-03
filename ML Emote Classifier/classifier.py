import json
import socket
import pandas as pd
import traceback
import warnings
import statsmodels.api as sm
import re

warnings.filterwarnings("ignore", category=RuntimeWarning)

with open("scraped-emotes.json", "r") as scrape_file:
    scraped_emotes = json.loads(scrape_file.read())

with open("emote-dict.json", "r") as emote_file:
    emote_data = json.loads(emote_file.read())

emotion_table: list = [
    ["optimism", "frivolity", "love", "gloat"],
    ["frustation", "disapproval", "envy", "remorse"],
    ["aggressiveness", "rejection", "rivalry", "contempt"],
    ["anxiety", "awe", "submission", "coercion"],
]

config_path: str = "../JSON Files/config.json"
with open(config_path, "r") as config_file:
    config_data = json.loads(config_file.read())


def emote_finder(message) -> list:
    global scraped_emotes
    message_list = [message][0].split()
    emote_list = []
    for emote in scraped_emotes:
        for word in message_list:
            if emote == word and emote not in emote_list:
                emote_list.append(emote)
    return emote_list


# This function can create averages of lists with four integers
def merge_lists(lists) -> list:
    merged_list = [0, 0, 0, 0]
    for array in lists:
        for i in range(len(array)):
            merged_list[i] += array[i]

    for i in range(len(merged_list)):
        if round(merged_list[i] / len(lists), 2) < -0.1:
            merged_list[i] = -1
        elif round(merged_list[i] / len(lists), 2) > 0.1:
            merged_list[i] = 1
        else:
            merged_list[i] = 0

    return merged_list


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


def classify_emotes(emote_array, last_evaluations) -> list:
    global emote_data
    dimensions = ["pleasentness", "attention", "sensitivity", "aptitude"]
    pl = []
    at = []
    se = []
    ap = []
    evaluation_numbers = []
    for i in range(len(last_evaluations)):
        evaluation_numbers.append(i)

    for evaluation in last_evaluations:
        pl.append(evaluation[0])
        at.append(evaluation[1])
        se.append(evaluation[2])
        ap.append(evaluation[3])

    df = pd.DataFrame(
        {
            "numbers": evaluation_numbers,
            dimensions[0]: pl,
            dimensions[1]: at,
            dimensions[2]: se,
            dimensions[3]: ap,
        }
    )

    prediction = [0, 0, 0, 0]
    if len(last_evaluations) >= 20:
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
            emote_dict_entry["times tested"] += 1
            emote_dict_entry["pleasentness"] = round(
                emote_dict_entry["pleasentness"] + prediction[0], 2
            )
            emote_dict_entry["attention"] = round(
                emote_dict_entry["attention"] + prediction[1], 2
            )
            emote_dict_entry["sensitivity"] = round(
                emote_dict_entry["sensitivity"] + prediction[2], 2
            )
            emote_dict_entry["aptitude"] = round(
                emote_dict_entry["aptitude"] + prediction[3], 2
            )
            print(f"Emote: {emote}")
            print(f"Prediction: {prediction}")
            emote_dict_entry["likely emotion"] = identify_emotion(emote_dict_entry)

        emote_values = [
            emote_dict_entry["pleasentness"] / emote_dict_entry["times tested"],
            emote_dict_entry["attention"] / emote_dict_entry["times tested"],
            emote_dict_entry["sensitivity"] / emote_dict_entry["times tested"],
            emote_dict_entry["aptitude"] / emote_dict_entry["times tested"],
        ]
        value_list.append(emote_values)

    average_values = merge_lists(value_list)
    return average_values


def identify_emotion(emote) -> str:
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
        round(emote["pleasentness"] / emote["times tested"], 2),
        round(emote["attention"] / emote["times tested"], 2),
        round(emote["sensitivity"] / emote["times tested"], 2),
        round(emote["aptitude"] / emote["times tested"], 2),
    ]
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
    if combination == 1:
        if value < 0:
            return 1
        else:
            return 0
    elif combination == 2:
        if value < 0:
            return 3
        else:
            return 2


def attempt_connection() -> None:
    global config_data
    channel = str(input("Channel to connect to: ")).lower()
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

            emote_array = emote_finder(msg)
            if emote_array != []:
                classification = classify_emotes(emote_array, last_evaluations)
                last_evaluations.append(classification)
            if len(last_evaluations) > max_evaluations:
                last_evaluations.pop(0)
            if messages_received % 500 == 0:
                with open("emote-dict.json", "w") as emote_file:
                    json.dump(emote_data, emote_file)
                    print("------ DATA SAVED ------")
                    print("")
                with open("emote-dict.json", "r") as emote_file:
                    emote_data = json.loads(emote_file.read())
            elif messages_received % 900 == 0:
                server.send(str.encode("PING tmi.twitch.tv\r\n", "utf-8"))


if __name__ == "__main__":
    attempt_connection()
