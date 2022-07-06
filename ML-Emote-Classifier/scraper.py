import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import os


def scrape_emotes():
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
    if formatted_emotes != []:
        with open("scraped-emotes.json", "w") as json_file:
            json.dump(formatted_emotes, json_file)
    else:
        print("Scraping has been unsuccessful")


def initialize_emote_dictionary():
    emote_dictionary = {}
    with open("scraped-emotes.json", "r") as scrape_data:
        emote_data = json.loads(scrape_data.read())
    print(emote_data)
    for emote in emote_data:
        emote_dictionary[emote] = {
            "likely emotion": "",
            "times tested": 1,
            "pleasentness": 0,
            "attention": 0,
            "sensitivity": 0,
            "aptitude": 0,
        }
    with open("emote-dict.json", "w") as emote_file:
        json.dump(emote_dictionary, emote_file)


def save_new_emotes():
    with open("emote-dict.json", "r") as emote_file:
        emote_dictionary = json.loads(emote_file.read())
    with open("scraped-emotes.json", "r") as scrape_data:
        scraped_data = json.loads(scrape_data.read())
    for emote in scraped_data:
        if emote not in emote_dictionary:
            emote_dictionary[emote] = {
                "likely emotion": "",
                "times tested": 1,
                "pleasentness": 0,
                "attention": 0,
                "sensitivity": 0,
                "aptitude": 0,
            }
    with open("emote-dict.json", "w") as emote_file:
        json.dump(emote_dictionary, emote_file)


def execute():
    emotes = scrape_emotes()
    print(type(emotes))
    save_top_emotes(emotes)
    if not os.path.exists("emote-dict.json"):
        initialize_emote_dictionary()
    else:
        save_new_emotes()


execute()
