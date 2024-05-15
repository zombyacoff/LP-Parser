import os
import re
import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange


launchTime = datetime.now()
launchTimeFormat = launchTime.strftime("%d-%m-%Y-%H-%M-%S")

# ”settings.yml” parsing
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

emailRegex = r"\S+@\S+\.\S+"
passwordRegex = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"

outputFolderName = "output"
outputFileName = f"{outputFolderName}/output-{launchTimeFormat}.yml"
outputFileNameComplete = f"{outputFolderName}/output-{launchTimeFormat}-complete.yml"
outputPattern = {
    "url": {},
    "login": {},
    "password": {}
}
outputIndex = 1

yearRange = launchTime.month if releaseDateBool and len(releaseDateYears) == 1 and launchTime.year in releaseDateYears else 12 
 

def progress_bar(current : int, total : int) -> None:
    percent = 100 * current/total
    round_percent = round(percent)
    bar = round_percent*"█"+(100-round_percent)*"#"

    print(f"\rParsing... {bar} \033[1;36m[{percent:.2f}%]\033[0m",
          end="\r")


def check_url(url : str) -> None:
    """
    The following code checks if the URL exists. 
    If the result is positive, the page is parsed to identify 
    the year the article was written. 
    This is done to verify if the conditions specified in the ”settings.yml” 
    file's ”release_date” section have been satisfied. 
    If the conditions are met, 
    the page will then be further parsed by the ”parse()” function.
    """
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
    """
    The following code writes the data generated 
    by the ”parse()” function to a file named ”output-__.yml”, 
    which was previously created in the ”main()” function. 
    All elements in the output are indexed, 
    thanks to the ”outputIndex” variable.
    """
    global outputIndex

    with open(outputFileName, "r") as file:
        output_data = yaml.safe_load(file)

    output_data["url"][outputIndex] = url
    output_data["login"][outputIndex] = login
    output_data["password"][outputIndex] = password   

    with open(outputFileName, "w") as file:
        yaml.dump(output_data, file)
    
    outputIndex += 1


def main():
    if not os.path.exists(outputFolderName):
        os.mkdir(outputFolderName)

    with open(outputFileName, "w") as file:
        yaml.dump(outputPattern, file)

    total_days = sum([monthrange(2020, month)[1] for month in range(1, yearRange+1)])

    counter = 1
    for month in range(1, yearRange+1):
        for day in range(1, monthrange(2020, month)[1]+1):
            for value in range(offsetValue):
                url_list = [url+f"-{month:02}-{day:02}-{value}" if value > 0 
                            else url+f"-{month:02}-{day:02}" 
                            for url in websitesList]
                for url in url_list:
                    check_url(url)
                progress_bar(counter, total_days*offsetValue)
                counter += 1

    os.rename(outputFileName, outputFileNameComplete)
    print(f"\n\n\033[1;32mSuccessfull complete!\033[0m --> {outputFileNameComplete}")


if __name__ == "__main__":
    main()