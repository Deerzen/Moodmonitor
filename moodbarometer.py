# Imported modules
from afinn import Afinn
import os
import streamlit  as st
import socket
import re
import time
import json


# Pinging the server regularly is necessary to prevent forced disconnections.
def ping_server():
    st.session_state["server"].send(str.encode("PING tmi.twitch.tv\r\n", "utf-8"))


def take_inputs():
    if st.button("Attempt connection"):
        attempt_connection()


def attempt_connection():
    config_path = "moodmonitor/config.json"
    with open (config_path, "r") as config_file:
        config_data = json.loads(config_file.read())
    try:
        st.session_state["server"] = socket.socket()
        st.session_state["server"].connect(("irc.chat.twitch.tv", 6667))
        st.session_state["server"].send(bytes("PASS " + config_data[0] + "\r\n", "utf-8"))
        st.session_state["server"].send(bytes("NICK " + config_data[1] + "\r\n", "utf-8"))
        st.session_state["server"].send(bytes("JOIN " + "#xqc" + "\r\n", "utf-8"))
        st.success("Connection to " + "XQC" + " appears to be successful")
        bot_loop()
    # Error message if unsuccessful.
    except Exception as e:
        ask_for_reset = st.error("Connection failed: " + str(e))


# Bot loop which receives all messages, decodes them and passes them to
# the analsis functions. Once the amount of handled messages reaches the desired
# threshold the emotion_report() gets called.
def bot_loop():
    placeholder = st.empty()
    last_messages = ["", "", "", "", "", ""]
    chat_msg = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
    while True:
        response = st.session_state["server"].recv(1024).decode("utf-8", "ignore")
        if "PING" in response:
            st.session_state["server"].send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            message = chat_msg.sub("", response)
            msg = message.split("\r\n")[0]
            msg = str(msg)
            last_messages.append(msg)
            last_messages.pop(0)
            placeholder.write(last_messages[5])


if __name__ == '__main__':
    take_inputs()
