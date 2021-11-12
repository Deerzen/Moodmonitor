# module import
from afinn import Afinn
import os
import socket
import re
import time
import json

# emoji data
# the chosen emotes are based upon the ranking of the most used emotes by streamlabs:
# tinyurl.com/datt2yau
# the emotion categories are second level emotions of the "Hourglass of Emotions" model
# for more acurate results this list should be validated through a survey
Optimism = [ "LUL", ":)", "FeelsGoodMan", "LULW", "SeemsGood", "LuL", "catJam", "sumParrot", "B)", "CurseLit", "yyjSmile", "pepeD", "blobDance", "forsenPls", "TRUEING", "eeveeDance", "dnyPls", "BloodTrail", "BlessRNG", "EZ", "pepeJAM", "jahParrot", "widepeepoHappy", "VoteYea", "PauseChamp", "CoolCat", "TriKool", "pepeJAMJAM", "LOLW", "PEPEDS", "PepoDance"]
Frustration = ["NotLikeThis", "DamnWart", "FailFish"]
Aggressiveness = ["SMOrc", "firneiSMOrc", "SwiftRage"]
Anxiety = ["WutFace", "monkaS", "monkaW"]
Frivolity = ["Kappa", "Kapp", "gaminaKappa", "KappaPride", "forseE", "TriHard", "WideHardo", "HeyGuys", "gachiBASS", "gachiHYPER", "gachiGASM", "FeelsOkayMan", "HandsUp", "FeelsButtsMan", "YEP", "WideHard", "DICKS", "Keepo", "GachiPls"]
Disapproval = ["D:", "cmonBruh"]
# Rejection = no emotes
Awe = ["PogChamp", "Pog", "PogU", "Clap", "5Head", "HYPERCLAP", "POGGERS", "PagChomp", "PagMan", "WAYTOODANK"]
Love = ["<3", "Kreygasm", "xqcL", "papaL", "nebelHERZ", "bleedPurple", "FeelsBirthdayMan", "VirtualHug", "TwitchUnity"]
# Envy = no emotes
Rivalry = ["s3r4Bund", "AYAYA", "NaM", "kiandoAYAYA", "No1", "KKona", "ANELE", "MingLee", "AYAYABASS", "VoHiYo"]
# Submission = no emotes
Gloat = ["OMEGALUL", "MEGALUL", "ZULUL", "KEKW", "chipsaKEK", "DuckerZ", "Jebaited", "EleGiggle", "PJSalt", "3Head", "OpieOP", "MrDestructoid", "peepoClap", "Pepega", "FeelsDankMan", "forsenCD", "PepeLaugh" , "pepeLaugh"]
Remorse = ["BibleThump", "FeelsBadMan", "flushE", ":(", "PepeHands", "AngelThump", "Sadge", "FeelsStrongMan", "widepeepoSad"]
Contempt = ["DansGame", "ResidentSleeper", "4Weirding", "haHAA", "sheydoN", "4Head", "BabyRage", "PogO", "WeirdChamp"]
# Coercion = no emotes

# emoji analysis global vars
# emotion count records how often an emotion has been used since last report
emotion_count = {"optimism": 0, "frustration": 0, "aggressiveness": 0, "anxiety": 0, "frivolity": 0, "disapproval": 0, "awe": 0, "love": 0, "rivalry": 0, "gloat": 0, "remorse": 0, "contempt": 0}

# sentiment analysis global vars
afn = Afinn(language="en", emoticons=True)
total_score = 0
score_amount = 0
avg_score = 0
outcome = 0
total_afinn_value = 0
afinn_mean = 0
squared_sum = 0
sentiment = "neutral"

# report global vars
report_number = 0
current_time = "00:00:00"
reports = {}

# check if an oauth token and account name has been saved
folder_path = "moodmonitor"
if not os.path.isdir(folder_path):
   os.makedirs(folder_path)
config_path = "moodmonitor/config.json"
if not os.path.exists(config_path):
    oauth = str(input("Enter a valid OAuth password (Can be generated at https://twitchapps.com/tmi/) "))
    user_name = str(input("Enter the user name of the associated Twitch account ")).lower()
    config_data = [oauth, user_name]
    with open(config_path, "w") as config_file:
        json.dump(config_data, config_file)
else:
    ask_for_reset = str(input("Do you want to reset the saved OAuth password and username? (y/n) "))
    if ask_for_reset == "y":
        os.remove(config_path)
    elif ask_for_reset == "n":
        pass
    else:
        print("Invalid input")
        quit()

# data for server connection
with open (config_path, "r") as config_file:
    config_data = json.loads(config_file.read())
connection_data = ("irc.chat.twitch.tv", 6667) # must not be changed
token = config_data[0] # token can be generated at twitchapps.com/tmi/
user = config_data[1] # twitch user name in lower cases that is associated with the token
channel = "#" + str(input("What channel do you want to monitor? ")).lower() # asking for the twitch channel the bot is supposed to join
readbuffer = ""

# vars for message handling
# report_interval dictates the amount of messages that are needed for a report
chat_msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
messages_since_report = 0
report_interval = int(input("On a how many messages should a report be based? "))

# tries to connect to the twitch IRC server with given information
try:
    server = socket.socket()
    server.connect(connection_data)
    server.send(bytes("PASS " + token + "\r\n", "utf-8"))
    server.send(bytes("NICK " + user + "\r\n", "utf-8"))
    server.send(bytes("JOIN " + channel + "\r\n", "utf-8"))
    connected = True
    print(server)
    print("")
    print("Connection to " + str(channel) + " appears to be successful")
    print("")
# error message if unsuccessful
except Exception as e:
    print(str(e))
    connected = False
    ask_for_reset = str(input("Connection failed. Do you want to reset the saved OAuth password? (y/n) "))
    if ask_for_reset == y:
        os.remove(config_path)

# analyzes sentiment of message with the Afinn Module
# once the amount of messages reaches desired threshold, an average is calculated for the report
# depending on the score a string is generated to make the sentiment easily readable
def sentiment_analysis(message):
    global total_score
    global score_amount
    global avg_score
    global outcome
    global sentiment

    score = afn.score(message)
    total_score += score
    score_amount += 1
    avg_score = total_score / score_amount
    avg_score = format(avg_score, ".2f")

    if score_amount >= report_interval:
        outcome = avg_score
        total_score = 0
        score_amount = 0
        if float(outcome) == 0.00:
            sentiment = "neutral"
        elif float(outcome) > 0.00:
            sentiment = "positive"
        elif float(outcome) < 0.00:
            sentiment = "negative"


# analyzes what emotions chat is expressing through emotes in the message
def emoji_analysis(message):
    dict = {0: [Optimism, "optimism"],
            1: [Frustration, "frustration"],
            2: [Aggressiveness, "aggressiveness"],
            3: [Anxiety, "anxiety"],
            4: [Frivolity, "frivolity"],
            5: [Disapproval, "disapproval"],
            6: [Awe, "awe"],
            7: [Love, "love"],
            8: [Rivalry, "rivalry"],
            9: [Gloat, "gloat"],
            10: [Remorse, "remorse"],
            11: [Contempt, "contempt"]
    }
    for i in dict:
        check_for_emotion(dict[i][0], dict[i][1], message)


# checks if message contains known emote and adds associated emotion to emotion_count
def check_for_emotion(array, string_name, msg):
    global emotion_count
    for i in range(len(array)):
        if array[i] in msg:
            emotion_count[string_name] += 1
            break


# checks for every emotion that has been used at least once since last report
# checks which emotion has been used the most
# requests the saving of all reports and initiates the printing of the current report
# resets emotions array / emotion count and pings the server
def emotion_report():
    global report_interval
    global emotion_count
    global sentiment
    global outcome
    global report_number
    global current_time
    global afinn_reports
    global afinn_mean
    global total_afinn_value
    global squared_sum

    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)

    report_number += 1
    total_afinn_value += float(outcome)
    afinn_mean = total_afinn_value / report_number
    afinn_deviation = float(outcome) - afinn_mean
    squared_sum += afinn_deviation ** 2
    afinn_variance = squared_sum / report_number
    emotions = []

    for emotion in emotion_count:
        if emotion_count[emotion] > 0:
            emotions.append(emotion)

    primary_emotion = 0
    emotion_string = "no known emotions"

    for i in emotions:
        if emotion_count[i] >= primary_emotion:
            number_string = int(emotion_count[i] / report_interval * 100)
            emotion_string = i + " (" + str(number_string) + "% of messages)"
            primary_emotion = emotion_count[i]

    save_report(report_number, outcome, emotion_string, afinn_mean, afinn_variance, current_time)
    print_report(report_number, current_time, sentiment, outcome, afinn_mean, afinn_variance, emotion_string)

    emotions = []
    emotion_count = {"optimism": 0, "frustration": 0, "aggressiveness": 0, "anxiety": 0, "frivolity": 0, "disapproval": 0, "awe": 0, "love": 0, "rivalry": 0, "gloat": 0, "remorse": 0, "contempt": 0}
    ping_server()


# safe the report to a JSON file
def save_report(r_number, oc, emotion, mean, variance, time):
    reports[int(r_number)] = [oc, emotion, mean, variance, time]
    path = "moodmonitor/data.json"
    with open(path, "w") as json_file:
        json.dump(reports, json_file)


# print the compiled report
def print_report(r_number, time, sent, oc, mean, variance, emotion):
    print("Report Nr. " + str(r_number) + " (" + str(time) + ")" + ":")
    print("Sentiment seems " + sent + " (Current Score: " + str(oc) + ", Mean: " + str(format(mean, '.2f')) + ", Variance: " + str(format(variance, '.2f')) + ")")
    print("Chat primarily expresses " + emotion)
    print(" ")


# pinging the server regularly is necessary to prevent forced disconnections
def ping_server():
    server.send(str.encode("PING tmi.twitch.tv\r\n", "utf-8"))


# bot loop which receives all messages, decodes them and passes them to the analsis functions
# once the amount of handled messages reaches the desired threshold the emotion_report() gets called
def bot_loop():
    global messages_since_report
    global report_interval

    while connected:
        response = server.recv(1024).decode("utf-8", "ignore")
        if "PING" in response:
            server.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        elif "PONG" in response:
            pass
        else:
            messages_since_report += 1
            message = chat_msg.sub("", response)
            msg = message.split("\r\n")[0]
            msg = str(msg)
            sentiment_analysis(msg)
            emoji_analysis(msg)
        if messages_since_report >= report_interval:
            emotion_report()
            messages_since_report = 0

# main loop
if __name__ == "__main__":
    bot_loop()
