import os
import yaml
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange

launchTime = datetime.now()
launchTimeFormat = launchTime.strftime("%d-%m-%Y-%H-%M-%S")

# ”settings.yml” parsing
with open("settings.yml") as file: 
    settings = yaml.safe_load(file)
    
offset = settings["offset"]
OFFSET_BOOL = offset["offset"]
OFFSET_VALUE = offset["value"] if OFFSET_BOOL else 1
releaseDate = settings["release_date"]
RELEASEDATE_BOOL = releaseDate["release_date"]
RELEASEDATE_YEARS = releaseDate["years"]
WEBSITES_LIST = settings["websites_list"]
EXCEPTIONS_LIST = settings["exceptions_list"]
forAdvancedUsers = settings["for_advanced_users"]
LOGIN_REGEX = rf"{forAdvancedUsers["login_regex"]}"
PASSWORD_REGEX = rf"{forAdvancedUsers["password_regex"]}"

OUTPUT_FOLDER_NAME = "output"
OUTPUTFILE_PATH = f"{OUTPUT_FOLDER_NAME}/output-{launchTimeFormat}.yml"
OUTPUTFILE_COMPLETE_PATH = f"{OUTPUT_FOLDER_NAME}/output-{launchTimeFormat}-complete.yml"
OUTPUTFILE_PATTERN = {
    "url": {},
    "login": {},
    "password": {}
}

YEAR_RANGE = launchTime.month if RELEASEDATE_BOOL and len(RELEASEDATE_YEARS) == 1 and launchTime.year in RELEASEDATE_YEARS else 12


async def process_url(url: str) -> None:
    """
    Sends a GET request to the specified URL and parses the HTML content.
    If the status code of the response is not 404, 
    it extracts the release date from the HTML content.
    If the release date is within the specified range or is a specified year,
    it extracts the website text and calls the 'parse' function to process the text.
    If the result is not an empty string, it calls the 'write_output' 
    function to write the parsed data to the output file.
    """
    async with aiohttp.ClientSession() as session:
        page = await session.get(url)

    if page.status != 404:
        soup = BeautifulSoup(await page.text(), "html.parser")
        release_date = int(soup.select_one("time").get_text("\n", strip=True)[-4:])
        if not RELEASEDATE_BOOL or release_date in RELEASEDATE_YEARS:
            website_text = [sentence for sentence in soup.stripped_strings]
            data = parse(website_text)
            if data[0] != "": write_output(url, data)


def parse(website_text: list[str]) -> list[str]:
    """
    This function parses the website text and returns the login and password.
    """
    login = ""
    password = ""

    for i, text in enumerate(website_text):
        email_match = re.findall(LOGIN_REGEX, text)
        if email_match and email_match[0] not in EXCEPTIONS_LIST: 
            login = email_match[0]
            if ":" in login:
                data = login.split(":")
                login = data[0]
                password = data[1]
                break
            if i < len(website_text)-4:
                for k in range(1, 4):
                    password_match = re.findall(PASSWORD_REGEX, website_text[i+k])
                    if password_match: 
                        password = password_match[0]
                        break

    return [login, password]


def write_output(url: str, data: list[str]) -> None:
    """
    This function writes the parsed data to the output file.
    """
    with open(OUTPUTFILE_PATH, "r") as file:
        output_data = yaml.safe_load(file)

    output_data["url"][write_output.counter] = url
    output_data["login"][write_output.counter] = data[0]
    output_data["password"][write_output.counter] = data[1] 

    with open(OUTPUTFILE_PATH, "w") as file:
        yaml.dump(output_data, file)
    
    write_output.counter += 1


async def main():
    if not os.path.exists(OUTPUT_FOLDER_NAME):
        os.mkdir(OUTPUT_FOLDER_NAME)

    with open(OUTPUTFILE_PATH, "w") as file:
        yaml.dump(OUTPUTFILE_PATTERN, file)

    write_output.counter = 1

    processes = []
    for month in range(2, YEAR_RANGE+1):
        for day in range(1, monthrange(2020, month)[1]+1):
            for value in range(OFFSET_VALUE):
                url_list = [url+f"-{month:02}-{day:02}-{value}" if value > 0 
                            else url+f"-{month:02}-{day:02}" 
                            for url in WEBSITES_LIST]
                for url in url_list:
                    process = asyncio.create_task(process_url(url))
                    processes.append(process)
    
    print("Parsing... ")
    await asyncio.gather(*processes)

    os.rename(OUTPUTFILE_PATH, OUTPUTFILE_COMPLETE_PATH)
    print(f"Successfully completed! ({datetime.now() - launchTime}) --> {OUTPUTFILE_COMPLETE_PATH}")


if __name__ == "__main__":
    asyncio.run(main())