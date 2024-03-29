# Imported modules
from afinn import Afinn
import streamlit as st
import pandas as pd
import os
import socket
import re
import time
import json

# Global variables
if "is_connected" not in st.session_state:
    st.session_state["is_connected"] = False
if "components_initialized" not in st.session_state:
    st.session_state["components_initialized"] = False

report_interval: int = 15
channel: str = ""
sentiment_data: dict = {
    "report number": [0],
    "afinn mean": [0],
    "afinn variance": [0],
    "current avg": [0],
}
sentiment_records: dict = {
    "total": 0.00,
    "scores": 0,
    "current avg": 0.00,
    "sentiment": "neutral",
    "report number": 0,
    "total afinn value": 0.00,
    "afinn mean": 0.00,
    "afinn deviation": 0.00,
    "squared sum": 0.00,
    "afinn variance": 0.00,
    "time": "00:00:00",
}
emotion_count: dict = {
    "optimism": 0,
    "frustration": 0,
    "aggressiveness": 0,
    "anxiety": 0,
    "frivolity": 0,
    "disapproval": 0,
    "rejection": 0,
    "awe": 0,
    "love": 0,
    "envy": 0,
    "rivalry": 0,
    "submission": 0,
    "gloat": 0,
    "remorse": 0,
    "contempt": 0,
    "coercion": 0,
}
emotion_data: dict = {
    "optimism": [0],
    "frustration": [0],
    "aggressiveness": [0],
    "anxiety": [0],
    "frivolity": [0],
    "disapproval": [0],
    "rejection": [0],
    "awe": [0],
    "love": [0],
    "envy": [0],
    "rivalry": [0],
    "submission": [0],
    "gloat": [0],
    "remorse": [0],
    "contempt": [0],
    "coercion": [0],
}
with open("JSON-Files/emote-data.json", "r", encoding="utf8") as emote_file:
    emote_data = json.loads(emote_file.read())


# Configuration of page title, icon and layout
st.set_page_config(page_title="Moodmonitor", page_icon="🖥️", layout="centered")

# CSS
# Hides row indices in tables.
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """
st.markdown(hide_table_row_index, unsafe_allow_html=True)
# Hides the streamlit style.
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# logo = st.image("https://raw.githubusercontent.com/Deerzen/Moodmonitor/main/logo.png")

config_path = "JSON-Files/config.json"
if not os.path.exists(config_path):
    with st.form(key="credentials"):
        explanation = st.markdown(
            "Enter your Twitch username and connect moodmonitor with a valid OAuth token "
            "(can easily be generated at https://twitchapps.com/tmi/)"
        )
        username = st.text_input("Twitch Username").lower()
        oauth = st.text_input("Twitch OAuth Token")
        if st.form_submit_button("Submit"):
            config_data = [oauth, username]
            with open(config_path, "w", encoding="utf8") as config_file:
                json.dump(config_data, config_file)

else:
    with st.form(key="configuration"):
        config_header = st.subheader("Configuration")
        status = st.empty()
        user_input = st.empty()
        connect = st.form_submit_button("Connect")
    status.info("No connection has been established yet")

    result_header = st.subheader("Result of analysis")
    afinn_result = st.empty()
    line_chart = st.empty()
    bar_chart = st.empty()
    chat_box = st.empty()
    afinn_result.info(
        "The generation of reports will start once you have connected to a valid"
        " Twitch channel and enough data has been collected."
    )
    st.session_state["components_initialized"] = True

# Pinging the server regularly is necessary to prevent forced disconnections.
# This function currently gets called with every third sentiment report.
def ping_server() -> None:
    st.session_state["server"].send(str.encode("PING tmi.twitch.tv\r\n", "utf-8"))


# Analyzes sentiment of message with the Afinn Module. Once the amount
# of messages reaches desired threshold, an average is calculated for the report.
# Depending on the score a string is generated to make the sentiment
# easily readable.
def sentiment_analysis(message) -> None:
    afn = Afinn(language="en", emoticons=True)
    sentiment_records["total"] += afn.score(message)
    sentiment_records["scores"] += 1


def emote_analysis(message) -> None:
    for emotion in emote_data:
        for emote in emote_data[emotion]:
            if emote in message:
                emotion_count[emotion.lower()] += 1
                return


# This funtion calculates the values for the sentiment report and updates
# the sentiment_records. Eventually it passes the values to display_report()
# and calls ping_server() every third report.
def calculate_report() -> None:
    # In this block the current afinn sentiment, the mean and the variance
    # are calculated.
    average = sentiment_records["total"] / sentiment_records["scores"]
    sentiment_records["current avg"] = format(average, ".2f")
    sentiment_records["total"] = 0
    sentiment_records["scores"] = 0
    if float(average) == 0.00:
        sentiment_records["sentiment"] = "neutral"
    elif float(average) > 0.00:
        sentiment_records["sentiment"] = "positive"
    elif float(average) < 0.00:
        sentiment_records["sentiment"] = "negative"

    t = time.localtime()
    sentiment_records["time"] = time.strftime("%H:%M:%S", t)
    sentiment_records["report number"] += 1
    sentiment_records["total afinn value"] += float(sentiment_records["current avg"])
    sentiment_records["afinn mean"] = (
        sentiment_records["total afinn value"] / sentiment_records["report number"]
    )
    sentiment_records["afinn deviation"] = (
        float(sentiment_records["current avg"]) - sentiment_records["afinn mean"]
    )
    sentiment_records["squared sum"] += sentiment_records["afinn deviation"] ** 2
    sentiment_records["afinn variance"] = (
        sentiment_records["squared sum"] / sentiment_records["report number"]
    )

    # Safes the current emotion count in a global variable for the bar chart
    for i in emotion_count:
        emotion_data[i].append(emotion_count[i])

    # In this block the dominant emotion is identified and how often it has
    # been expressed relatively. Finally the emotion_count is reset
    # for the next interval.
    dominant_emotion = max(emotion_count, key=emotion_count.get)
    emotion_percentage = format(
        emotion_count[dominant_emotion] / report_interval * 100, ".2f"
    )
    if emotion_percentage == 0.00:
        dominant_emotion = "unknown"
    for i in emotion_count:
        emotion_count[i] = 0

    # This part of the function sends the calculated values to the
    # display report function and pings the server every third report.
    display_report(sentiment_records, dominant_emotion, emotion_percentage)
    if sentiment_records["report number"] % 3 == 0:
        ping_server()


def calculate_line_chart() -> pd.core.frame.DataFrame:
    chart_data: dict = {
        "mean": sentiment_data["afinn mean"],
        "variance": sentiment_data["afinn variance"],
        "score": sentiment_data["current avg"],
    }
    return pd.DataFrame(chart_data, index=sentiment_data["report number"])


def calculate_bar_chart() -> pd.core.frame.DataFrame:
    return pd.DataFrame(data=emotion_data)


# This function simply updates the display for the most recent report
# with the calculated sentiment data.
def display_report(value_dict, emotion, percentage) -> None:
    line1: str = (
        f"Report Nr. {str(value_dict['report number'])} ({str(value_dict['time'])}):"
    )
    line2: str = (
        f"Sentiment seems {value_dict['sentiment']} (Current Score:"
        f" {str(value_dict['current avg'])}, Mean:"
        f" {str(format(value_dict['afinn mean'], '.2f'))}, Variance:"
        f" {str(format(value_dict['afinn variance'], '.2f'))})."
    )
    line3: str = (
        f"The dominant emotion appears to be {emotion}"
        f" ({percentage} of messages contain this emotion)."
    )
    afinn_result.info(f"{line1}\n{line2}\n{line3}")
    dict_key: list = ["report number", "afinn mean", "afinn variance", "current avg"]
    for i in dict_key:
        if i == "report number":
            sentiment_data[i].append(int(value_dict[i]))
        else:
            sentiment_data[i].append(float(value_dict[i]))


# User input for the channel to connect to and button
# to establish the connection.
def take_inputs() -> None:
    global channel
    channel = user_input.text_input("Twitch channel to monitor").lower()
    if connect:  # Meaning the connect button has been pressed
        if channel != "":
            attempt_connection()
        else:
            status.info("Please specify a channel to connect to and press enter.")


# Simply reads the config data from a json file and returns the content.
def read_config() -> list:
    path: str = "JSON-Files/config.json"
    with open(path, "r", encoding="utf8") as file:
        data = json.loads(file.read())
    return data


# Uses the provided data to connect to a Twitch IRC channel.
def attempt_connection() -> None:
    config = read_config()
    try:
        st.session_state["server"] = socket.socket()
        st.session_state["server"].connect(("irc.chat.twitch.tv", 6667))
        st.session_state["server"].send(bytes("PASS " + config[0] + "\r\n", "utf-8"))
        st.session_state["server"].send(bytes("NICK " + config[1] + "\r\n", "utf-8"))
        st.session_state["server"].send(bytes(f"JOIN #{channel}" + "\r\n", "utf-8"))
        st.session_state["is_connected"] = True
        bot_loop()
    except Exception as e:
        error_message = status.error(f"Connection to {channel} failed: {str(e)}")


# Bot loop which receives all messages, decodes them and passes them to
# the analsis functions. Once the amount of handled messages reaches the desired
# threshold the emotion_report() gets called.
def bot_loop() -> None:
    config = read_config()
    messages_since_report: int = 0
    processed_messages: int = 0
    last_messages: dict = {
        "Messages": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    }
    ignore = ["JOIN", ":Welcome", "PING", "PONG"]
    chat_msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    connection_msg = ":tmi.twitch.tv 001 " + config[1] + " :Welcome, GLHF!"

    while st.session_state["is_connected"]:
        response = st.session_state["server"].recv(1024).decode("utf-8", "ignore")
        if "PING" in response:
            st.session_state["server"].send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            message = chat_msg.sub("", response)
            msg = message.split("\r\n")[0]
            msg = str(msg)

            if connection_msg in msg:
                status.success(f"Connection to {channel} appears to be successful")

            if all(ele not in message for ele in ignore):
                sentiment_analysis(msg)
                emote_analysis(msg)
                messages_since_report += 1

                if len(last_messages["Messages"]) >= 10:
                    last_messages["Messages"].pop(0)
                    last_messages["Messages"].append(msg)
                    processed_messages += 1

            if messages_since_report >= report_interval:
                calculate_report()
                line_chart.line_chart(calculate_line_chart())
                bar_chart.bar_chart(calculate_bar_chart())
                messages_since_report = 0

            chat_data = pd.DataFrame(last_messages)
            with chat_box.empty():
                st.table(chat_data)


if (
    __name__ == "__main__"
    and os.path.exists(config_path)
    and st.session_state["components_initialized"]
):
    take_inputs()
