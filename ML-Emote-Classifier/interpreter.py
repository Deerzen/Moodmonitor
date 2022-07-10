# This table enables the script later to identify the most likely emotion
# based on the collected information on pleasentness, attention, sensitivity
# and aptitude.
EMOTION_TABLE: list = [
    ["optimism", "frivolity", "love", "gloat"],
    ["frustation", "disapproval", "envy", "remorse"],
    ["aggressiveness", "rejection", "rivalry", "contempt"],
    ["anxiety", "awe", "submission", "coercion"],
]


def identify_emotion(emote, is_printing) -> str:
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
        print(f"Likely emotion: {EMOTION_TABLE[key[0]][key[1]]}")
        print("")
    return EMOTION_TABLE[key[0]][key[1]]


def find_data_keys(pair, values) -> list:
    """This function identifies the right keys to find the dominant emotion
    in the EMOTION_TABLE"""

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


def return_key(combination, value) -> int:
    """Checks for negative or positive values for one of two possible combinations
    and returns the appropriate key."""

    return_values = {1: [1, 0], 2: [3, 2]}

    if value < 0:
        return return_values[combination][0]
    else:
        return return_values[combination][1]
