import os
import re
import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange


launchTime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

with open("settings.yml") as file: 
    settings = yaml.safe_load(file)

exceptions = settings["exceptions"]

offset = settings["offset"]
offsetBool = offset["offset"]
offsetValue = offset["value"] if offsetBool else 1

releaseDate = settings["release_date"]
releaseDateBool = releaseDate["release_date"]
releaseDateYears = releaseDate["years"]

websitesList = settings["websites_list"]

microsoftLoginUrl = "https://login.live.com/ppsecure/secure.srf"

emailRegex = r"\S+@\S+\.\S+"
passwordRegex = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"

outputExample = {
    "url": {},
    "login": {},
    "password": {}
}
outputIndex = 1

 
def progress_bar(current : int, total : int) -> None:
    percent = 100 * current/total
    round_percent = round(percent)

    print(f"\rParsing... {round_percent*"█"+(100-round_percent)*"#"} [{percent:.2f}%]", end="\r")


def check_url(url : str) -> None:
    page = requests.get(url)

    if page.status_code != 404:
        soup = BeautifulSoup(page.text, "html.parser")
        release_date = int(soup.select_one("time").get_text("\n", strip=True)[-4:])
        if not releaseDateBool or release_date in releaseDateYears:
            parse(url, soup)


def parse(url : str, soup : BeautifulSoup) -> None:
    website_text = [sentence for sentence in soup.stripped_strings]

    for i, current in enumerate(website_text):
        login = re.findall(emailRegex, current)
        if login and login[0] not in exceptions:
            password = website_text[i+1].split()[-1] if re.findall(passwordRegex, website_text[i+1]) else website_text[i+2]
            write_output(url, login[0], password)
            break


def write_output(url : str, login : str, password : str) -> None:
    global outputIndex

    with open(f"output-{launchTime}.yaml", "r") as file:
        outputData = yaml.safe_load(file)

    outputData["url"][outputIndex] = url
    outputData["login"][outputIndex] = login
    outputData["password"][outputIndex] = password   

    with open(f"output-{launchTime}.yaml", "w") as file:
        yaml.dump(outputData, file)
    
    outputIndex += 1

def main():
    with open(f"output-{launchTime}.yaml", "w") as file:
        yaml.dump(outputExample, file)

    counter = 1
    for month in range(1, 13):
        for day in range(1, monthrange(2020, month)[1]+1):
            for value in range(offsetValue):
                url_list = [url+f"-{month:02}-{day:02}-{value}" if value > 0 
                            else url+f"-{month:02}-{day:02}" 
                            for url in websitesList]
                for url in url_list:
                    check_url(url)
                progress_bar(counter, 366*offsetValue)
                counter += 1

    """
    with open("output-15-05-2024-14-34-30.yaml", "r") as file:
        microsoftData = yaml.safe_load(file)
        for i in range(len(microsoftData["password"])):
            microsoft_check([microsoftData["login"][i], microsoftData["password"][i]])
    """

    os.rename(f"output-{launchTime}.yaml", f"output-{launchTime}-complete.yaml")
    print(f"\nSuccessfull complete! >> output-{launchTime}-complete.yaml")


if __name__ == "__main__":
    main()