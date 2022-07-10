import os
import json
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver

dictionary_format = {
    "likely emotion": "",
    "times tested": [1, 1, 1, 1],
    "pleasentness": 0,
    "attention": 0,
    "sensitivity": 0,
    "aptitude": 0,
}


def scrape_emotes():
    os.environ["MOZ_HEADLESS"] = "1"
    driver = webdriver.Firefox()
    driver.get("https://stats.streamelements.com/c/global")
    soup = BeautifulSoup(driver.page_source, "lxml")
    emotes = soup.find_all("div", attrs={"class": "c0111 c0116 c01134"})
    driver.quit()

    return emotes


def save_top_emotes(emotes) -> bs4.element.ResultSet:
    formatted_emotes = []
    index = 0
    for emote in emotes:
        index += 1
        text = str(emote)
        start = text.index('">') + 2
        end = text.index("</")
        substring = text[start:end]
        if (
            index > 100
            and "#" not in substring
            and "!" not in substring
            and substring != ""
        ):
            formatted_emotes.append(substring)
    if formatted_emotes:
        with open("scraped-emotes.json", "w", encoding="utf8") as json_file:
            json.dump(formatted_emotes, json_file)
        print("Scraping has been successful")
    elif not formatted_emotes:
        print("Scraping has been unsuccessful")


def initialize_emote_dictionary():
    emote_dictionary = {}
    with open("scraped-emotes.json", "r", encoding="utf8") as scrape_data:
        emote_data = json.loads(scrape_data.read())
    for emote in emote_data:
        emote_dictionary[emote] = dictionary_format
    with open("emote-dict.json", "w", encoding="utf8") as emote_file:
        json.dump(emote_dictionary, emote_file)


def save_new_emotes():
    with open("emote-dict.json", "r", encoding="utf8") as emote_file:
        emote_dictionary = json.loads(emote_file.read())
    with open("scraped-emotes.json", "r", encoding="utf8") as scrape_data:
        scraped_data = json.loads(scrape_data.read())
    for emote in scraped_data:
        if emote not in emote_dictionary:
            emote_dictionary[emote] = dictionary_format
    with open("emote-dict.json", "w", encoding="utf8") as emote_file:
        json.dump(emote_dictionary, emote_file)


def execute():
    emotes = scrape_emotes()
    save_top_emotes(emotes)
    if os.path.exists("emote-dict.json"):
        save_new_emotes()
    else:
        initialize_emote_dictionary()
