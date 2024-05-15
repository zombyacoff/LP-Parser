import os
import re
import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange


launchTime = datetime.now()
launchTimeFormat = launchTime.strftime("%d-%m-%Y-%H-%M-%S")

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

yearRange = launchTime.month if releaseDateBool and len(releaseDateYears) == 1 and launchTime.year in releaseDateYears else 12 
 
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

    with open(f"output-{launchTimeFormat}.yaml", "r") as file:
        output_data = yaml.safe_load(file)

    output_data["url"][outputIndex] = url
    output_data["login"][outputIndex] = login
    output_data["password"][outputIndex] = password   

    with open(f"output-{launchTimeFormat}.yaml", "w") as file:
        yaml.dump(output_data, file)
    
    outputIndex += 1

def main():
    with open(f"output-{launchTimeFormat}.yaml", "w") as file:
        yaml.dump(outputExample, file)

    month_in_days = lambda month_value: sum([monthrange(2020, month_value)[1] for _ in range(month_value)])

    counter = 1
    for month in range(1, yearRange):
        for day in range(1, monthrange(2020, month)[1]+1):
            for value in range(offsetValue):
                url_list = [url+f"-{month:02}-{day:02}-{value}" if value > 0 
                            else url+f"-{month:02}-{day:02}" 
                            for url in websitesList]
                for url in url_list:
                    check_url(url)
                progress_bar(counter, month_in_days(yearRange)*offsetValue)
                counter += 1

    os.rename(f"output-{launchTimeFormat}.yaml", f"output-{launchTimeFormat}-complete.yaml")
    print(f"\nSuccessfull complete! >> output-{launchTimeFormat}-complete.yaml")


if __name__ == "__main__":
    main()