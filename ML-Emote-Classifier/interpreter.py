# This table contains the emotions for each dimension going from very positive (1)
# to very negative (-1).
EMOTION_TABLE: list = [
    ["ecstasy", "joy", "contentment", "melancholy", "sadness", "grief"],
    ["bliss", "calmness", "serenity", "annoyance", "anger", "rage"],
    ["enthusiasm", "eagerness", "responsiveness", "anxiety", "fear", "terror"],
    ["delight", "pleasentness", "acceptance", "dislkike", "disgust", "loathing"],
]


def identify_emotion(emote, is_printing) -> list:
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
        for key in combinations:
            if value >= combinations[key]:
                emotions.append(EMOTION_TABLE[index][key])
                index += 1
                break

    if is_printing:
        print(f"Times tested: {emote['times tested']}")
        print(
            f"In: {evaluation[0]}, Te: {evaluation[1]}, Se: {evaluation[2]}, At: {evaluation[3]}"
        )
        print(f"Emotions: {emotions}")
        print("")

    return emotions
