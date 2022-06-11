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
report_interval = 10
reports = {}
sentiment_records = {
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
    "time": "00:00:00"
}

# CSS
# Hide row indices in tables.
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# Streamlit elements for the display of the most recent report.
# The content will be updated in display_report().
r1 = st.empty()
r2 = st.empty()
r1.write("")
r2.write("")


# Pinging the server regularly is necessary to prevent forced disconnections.
# This function currently gets called with every third sentiment report.
def ping_server():
    st.session_state["server"].send(
        str.encode("PING tmi.twitch.tv\r\n", "utf-8"))


# Analyzes sentiment of message with the Afinn Module. Once the amount
# of messages reaches desired threshold, an average is calculated for the report.
# Depending on the score a string is generated to make the sentiment
# easily readable.
def sentiment_analysis(message):
    global sentiment_records
    global report_interval

    afn = Afinn(language="en", emoticons=True)
    sentiment_records["total"] += afn.score(message)
    sentiment_records["scores"] += 1
    print(message)
    print(sentiment_records)
    print("")


# This funtion calculates the values for the sentiment report and updates
# the sentiment_records. Eventually it passes the values to display_report()
# and calls ping_server() every third report.
def calculate_report():
    global sentiment_records

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
    sentiment_records["total afinn value"] += float(
        sentiment_records["current avg"])
    sentiment_records["afinn mean"] = sentiment_records["total afinn value"] / \
        sentiment_records["report number"]
    sentiment_records["afinn deviation"] = float(
        sentiment_records["current avg"]) - sentiment_records["afinn mean"]
    sentiment_records["squared sum"] += sentiment_records["afinn deviation"] ** 2
    sentiment_records["afinn variance"] = sentiment_records["squared sum"] / \
        sentiment_records["report number"]

    display_report(sentiment_records)
    if sentiment_records["report number"] % 3 == 0:
        ping_server()


# This function simply updates the display for the most recent report
# with the calculated sentiment data.
def display_report(value_dict):
    r1.write("Report Nr. " +
             str(value_dict["report number"]) +
             " (" +
             str(value_dict["time"]) +
             ")" +
             ":")
    r2.write("Sentiment seems " +
             value_dict["sentiment"] +
             " (Current Score: " +
             str(value_dict["current avg"]) +
             ", Mean: " +
             str(format(value_dict["afinn mean"], '.2f')) +
             ", Variance: " +
             str(format(value_dict["afinn variance"], '.2f')) +
             ")")

# User input for the channel to connect to and button
# to establish the connection.
def take_inputs():
    channel = st.text_input("Channel to monitor")
    if st.button("Attempt connection"):
        attempt_connection()


# Simply reads the config data from a json file and returns the content.
def read_config():
    config_path = "moodmonitor/config.json"
    with open(config_path, "r") as config_file:
        config_data = json.loads(config_file.read())
    return config_data


# Uses the provided data to connect to a Twitch IRC channel.
def attempt_connection():
    config_data = read_config()
    try:
        st.session_state["server"] = socket.socket()
        st.session_state["server"].connect(("irc.chat.twitch.tv", 6667))
        st.session_state["server"].send(
            bytes("PASS " + config_data[0] + "\r\n", "utf-8"))
        st.session_state["server"].send(
            bytes("NICK " + config_data[1] + "\r\n", "utf-8"))
        st.session_state["server"].send(
            bytes("JOIN " + "#xqc" + "\r\n", "utf-8"))
        bot_loop()
    # Error message if unsuccessful.
    except Exception as e:
        ask_for_reset = st.error("Connection failed: " + str(e))


# Bot loop which receives all messages, decodes them and passes them to
# the analsis functions. Once the amount of handled messages reaches the desired
# threshold the emotion_report() gets called.
def bot_loop():
    global report_interval
    success_note = st.empty()
    chat_box = st.empty()
    config_data = read_config()
    messages_since_report = 0
    processed_messages = 0
    last_messages = {"Messages": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]}
    ignore = ["JOIN", ":Welcome", "PONG", "ACTION"]
    chat_msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    connection_msg = ":tmi.twitch.tv 001 " + \
        config_data[1] + " :Welcome, GLHF!"

    while True:
        response = st.session_state["server"].recv(
            1024).decode("utf-8", "ignore")
        if "PING" in response:
            st.session_state["server"].send(
                "PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            message = chat_msg.sub("", response)
            msg = message.split("\r\n")[0]
            msg = str(msg)

            if connection_msg in msg:
                success_note.success(
                    "Connection to " +
                    "XQC" +
                    " appears to be successful")

            if not any(ele in message for ele in ignore):
                sentiment_analysis(msg)
                messages_since_report += 1

            if messages_since_report >= report_interval:
                calculate_report()
                messages_since_report = 0

            if len(last_messages["Messages"]) >= 10:
                last_messages["Messages"].pop(0)
            last_messages["Messages"].append(msg)
            processed_messages += 1
            
            chat_data = pd.DataFrame(last_messages)
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            chat_box.table(chat_data)


if __name__ == '__main__':
    take_inputs()
