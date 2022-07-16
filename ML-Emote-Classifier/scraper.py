"""BS4 and Selenium are need for webscraping. The data_processor module is imported
for convenience and readability"""

import os
from bs4 import BeautifulSoup
from selenium import webdriver
import data_processor

SCRAPE_PATH = "../JSON-Files/scraped-emotes.json"
DICTIONARY_PATH = "../JSON-Files/emote-dict.json"
dictionary_format = {
    "likely emotion": "",
    "times tested": [1, 1, 1, 1],
    "pleasentness": 0,
    "attention": 0,
    "sensitivity": 0,
    "aptitude": 0,
}


def scrape_emotes():
    """Visits stats.streamelements.com headless with selenium, reads the site
    with beautiful soup and returns found emotes"""

    os.environ["MOZ_HEADLESS"] = "1"
    driver = webdriver.Firefox()
    driver.get("https://stats.streamelements.com/c/global")
    soup = BeautifulSoup(driver.page_source, "lxml")
    emotes = soup.find_all("div", attrs={"class": "c0111 c0116 c01134"})
    driver.quit()

    return emotes


def save_top_emotes(emotes) -> None:
    """filters the scraped elements for just the emotes that we need
    and writes them to a json file"""

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
        data_processor.write_json(formatted_emotes, SCRAPE_PATH)
        print("Scraping has been successful")
    elif not formatted_emotes:
        print("Scraping has been unsuccessful")


def initialize_emote_dictionary() -> None:
    """Writes the scraped emotes in a dictionary in the defined format"""

    emote_dictionary = {}
    emote_data = data_processor.read_json(SCRAPE_PATH)
    for emote in emote_data:
        emote_dictionary[emote] = dictionary_format
    data_processor.write_json(emote_dictionary, DICTIONARY_PATH)


def save_new_emotes() -> None:
    """Takes the scraped emotes, compares them to the already collected
    data and appends new ones"""

    emote_dictionary = data_processor.read_json(DICTIONARY_PATH)
    scraped_data = data_processor.read_json(SCRAPE_PATH)
    for emote in scraped_data:
        if emote not in emote_dictionary:
            emote_dictionary[emote] = dictionary_format
    data_processor.write_json(emote_dictionary, DICTIONARY_PATH)


def execute() -> None:
    """Calls the functions in correct order"""

    emotes = scrape_emotes()
    save_top_emotes(emotes)
    if os.path.exists(DICTIONARY_PATH):
        save_new_emotes()
    else:
        initialize_emote_dictionary()
