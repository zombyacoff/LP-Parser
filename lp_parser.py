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

launchTime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

with open("settings.yml") as s: settings = yaml.safe_load(s)

exceptions = settings["exceptions"]

offset = settings["offset"]
offsetBool = offset["offset"]
offsetValue = offset["value"] if offsetBool else 1

releaseDate = settings["release_date"]
releaseDateBool = releaseDate["release_date"]
releaseDateYears = releaseDate["years"]

websitesList = settings["websites_list"]

s.close()

microsoftLoginUrl = "https://login.live.com/ppsecure/secure.srf"

emailRegex = r"\S+@\S+\.\S+"
passwordRegex = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"

def progress_bar(current : int, total : int) -> None:
    percent = 100 * current/total
    round_percent = round(percent)

    print(f"\r{round_percent*"█"+(100-round_percent)*"#"} [{percent:.2f}%]", end="\r")

"""
def microsoft_check(data : list[str]) -> bool:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)
    driver.get(microsoftLoginUrl)
    time.sleep(2)
    driver.find_element(By.ID,"i0116").send_keys(data[0])
    time.sleep(1)
    driver.find_element(By.XPATH,"//*[@id='idSIButton9']").click()
    time.sleep(1)
    driver.find_element(By.ID,"i0118").send_keys(data[1])
    time.sleep(1)
    driver.find_element(By.XPATH,"//*[@id='idSIButton9']").click()
    time.sleep(1)
    try:
        if driver.find_element(By.ID,"i0118Error") or driver.find_element(By.ID,"idTD_Error") or driver.find_element(By.ID,"iSelectProofTitle"):
            return False
    except:
        return True
    driver.close()
"""

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
            write_file([url, login[0], password])
            break

def write_file(values : list[str]) -> None:
    for value in values:
        logFile.write(value+"\n")
        logFile.flush()

def main():
    global logFile
    logFile = open(f"{launchTime}.txt", "w+")

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

    logFile.close()
    os.rename(f"{launchTime}.txt", f"{launchTime}_complete.txt")
    print(f"\nSuccessfull complete! >> {launchTime}_complete.txt")

if __name__ == "__main__":
    main()