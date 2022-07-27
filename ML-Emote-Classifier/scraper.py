"""BS4 and Selenium are need for webscraping. The data_processor module is imported
for convenience and readability"""

import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import data_processor

SCRAPE_PATH = "../JSON-Files/scraped-emotes.json"
DICTIONARY_PATH = "../JSON-Files/emote-dict.json"
dictionary_format = {
    "emotions": ["", "", "", ""],
    "times tested": [1, 1, 1, 1],
    "introspection": 0,
    "temper": 0,
    "sensitivity": 0,
    "attitude": 0,
}


def find_top_channels():
    url = "https://gql.twitch.tv/gql#origin=twilight"

    payload = '[{"operationName":"BrowsePage_Popular","variables":{"imageWidth":50,"limit":30,"platformType":"all","options":{"sort":"VIEWER_COUNT","freeformTags":null,"tags":[],"recommendationsContext":{"platform":"web"},"requestID":"JIRA-VXP-2397"},"sortTypeIsRecency":false,"freeformTagsEnabled":false},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"267d2d2a64e0a0d6206c039ea9948d14a9b300a927d52b2efc52d2486ff0ec65"}}},{"operationName":"PersonalSections","variables":{"input":{"sectionInputs":["RECOMMENDED_SECTION"],"recommendationContext":{"platform":"web","clientApp":"twilight","location":"directory.popular","referrerDomain":"www.twitch.tv","viewportHeight":927,"viewportWidth":906,"channelID":null,"channelLanguage":null,"categoryID":null,"channelUptime":null,"lastChannelID":null,"lastCategoryID":null,"pageviewContent":null,"pageviewContentType":null,"pageviewLocation":"directory.popular","pageviewMedium":null,"previousPageviewContent":null,"previousPageviewContentType":null,"previousPageviewLocation":"directory.popular","previousPageviewMedium":null}},"creatorAnniversariesExperimentEnabled":false,"sideNavActiveGiftExperimentEnabled":false},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"469b047f12eef51d67d3007b7c908cf002c674825969b4fa1c71c7e4d7f1bbfb"}}}]'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "Accept-Encoding": "gzip, deflate, br",
        "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko",
        "X-Device-Id": "5J6ImxCfnsiaqjhXzJKC4gtgXS3yoYt0",
        "Client-Version": "9efb637d-cf23-4752-b716-b8a1f71f2bbc",
        "Client-Session-Id": "5390e5ca4a39fdd3",
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://www.twitch.tv",
        "DNT": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    channels = []
    dictionaries = response.json()[0]["data"]["streams"]["edges"]
    for dictionary in dictionaries:
        channels.append(str(dictionary["node"]["broadcaster"]["displayName"]))
    return channels


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
