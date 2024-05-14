from bs4 import BeautifulSoup
import requests
import os
import re
import yaml
from datetime import datetime
from calendar import monthrange

launchTime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

try: logFile = open(f"output/{launchTime}.txt", 'w+')
except: os.mkdir("output"); logFile = open(f"output/{launchTime}.txt", 'w+')

with open("settings.yml") as fh: settings = yaml.safe_load(fh)
websites = settings["websites_list"]
offset = settings["offset"]
offsetBool = offset["offset"]
offsetValue = offset["value"]
releaseDate = settings["release_date"]
releaseDateBool = releaseDate["release_date"]
if releaseDateBool: rightYear = [year for year in releaseDate["years"]]
else: rightYear = []
fh.close()

def progressBar(current : int, total : int) -> None:
    percent = 100 * current/total
    print(f"\r{round(percent)*'█'+(100-round(percent))*'#'} [{round(percent,1)}%]", end='\r')

def parse(url : str) -> None:
    page = requests.get(url)
    if page.status_code != 404:
        soup = BeautifulSoup(page.text, "html.parser")
        release_date = int(soup.select_one("time").get_text('\n', strip=True)[-4:])
        if not releaseDateBool or release_date in rightYear:
            text = [i for i in soup.stripped_strings]
            for i in range(len(text)):
                login = re.findall(r"\S+@\S+\.\S+", text[i])
                if login and login != ["dmca@telegram.org"]:
                    if len(text[i+1]) < 14: password = text[i+2]
                    else: password = text[i+1].split()[-1]
                    logFile.write('\n'.join([url, *login, password, '\n'])); logFile.flush()

def main():
    counter = 1
    for month in range(1, 13):
        for day in range(1, monthrange(2020, month)[1]+1):
            websitesList = [url+f"-{month:02}-{day:02}" for url in websites]
            if offsetBool:
                for i in range(len(websites)):
                    for k in range(2, offsetValue+1):
                        websitesList.append([url+f"-{month:02}-{day:02}-{k}" for url in websites][i])
            for url in websitesList: parse(url)
            progressBar(counter, 366)
            counter += 1

    logFile.close()
    os.rename(f"output/{launchTime}.txt", f"output/{launchTime}_complete.txt")
    print(f"\nSuccessfull complete! >> output/{launchTime}_complete.txt")

if __name__ == "__main__":
    main()