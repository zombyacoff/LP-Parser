import os
import yaml
import requests
import rust_module
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


OUTPUT_FOLDER_NAME = "output"
OUTPUTFILE_PATH = f"{OUTPUT_FOLDER_NAME}/output-{launchTimeFormat}.yml"
OUTPUTFILE_COMPLETE_PATH = f"{OUTPUT_FOLDER_NAME}/output-{launchTimeFormat}-complete.yml"
OUTPUTFILE_PATTERN = {
    "url": {},
    "login": {},
    "password": {}
}
#OUTPUTFILE_PATTERN_KEYS = OUTPUTFILE_PATTERN.keys()

EMAIL_REGEX = r"\S+@\S+\.\S+"
PASSWORD_REGEX = r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}"

YEAR_RANGE = launchTime.month if RELEASEDATE_BOOL and len(RELEASEDATE_YEARS) == 1 and launchTime.year in RELEASEDATE_YEARS else 12 
 

def progress_bar(
    doing_something: str, 
    current: int, 
    total: int
) -> None:
    percent = 100 * current/total
    round_percent = round(percent)
    bar = round_percent*"█"+(100-round_percent)*"#"

    print(f"\r{doing_something} {bar} \033[1;36m[{percent:.2f}%]\033[0m",
          end="\r")


def check_url(url: str) -> bool:
    """
    The following code checks if the URL exists. 
    If the result is positive, the page is parsed 
    to identify the year the article was written. 
    This is done to verify if the conditions specified 
    in the ”settings.yml” file's ”release_date” 
    section have been satisfied.
    :return: bool
    """
    global soup
    page = requests.get(url)

    if page.status_code != 404:
        soup = BeautifulSoup(page.text, "html.parser")
        release_date = int(soup.select_one("time").get_text("\n", strip=True)[-4:])
        return not RELEASEDATE_BOOL or release_date in RELEASEDATE_YEARS
    return False


def parse(url: str) -> None:
    website_text = [sentence for sentence in soup.stripped_strings]
    """
    for i, current in enumerate(website_text):
        login = re.findall(EMAIL_REGEX, current)
        if login and login[0] not in EXCEPTIONS_LIST:
            password = website_text[i+1].split()[-1] if re.findall(PASSWORD_REGEX, website_text[i+1]) else website_text[i+2]
            write_output(url, login[0], password)
            break
    """
    result = rust_module.parse(EXCEPTIONS_LIST, website_text)
    if result[0] != "":
        write_output(url, result)


def write_output(url: str, data: list[str]) -> None:
    """
    The following code writes the data generated 
    by the ”parse()” function to a file named ”output-__.yml”, 
    which was previously created in the ”main()” function. 
    """
    with open(OUTPUTFILE_PATH, "r") as file:
        output_data = yaml.safe_load(file)

    output_data["url"][write_output.counter] = url
    output_data["login"][write_output.counter] = data[0]
    output_data["password"][write_output.counter] = data[1] 

    with open(OUTPUTFILE_PATH, "w") as file:
        yaml.dump(output_data, file)
    
    write_output.counter += 1

write_output.counter = 1


def main():
    if not os.path.exists(OUTPUT_FOLDER_NAME):
        os.mkdir(OUTPUT_FOLDER_NAME)

    with open(OUTPUTFILE_PATH, "w") as file:
        yaml.dump(OUTPUTFILE_PATTERN, file)

    total_days = sum([monthrange(2020, month)[1] for month in range(1, YEAR_RANGE+1)])

    counter = 1
    for month in range(1, YEAR_RANGE+1):
        for day in range(1, monthrange(2020, month)[1]+1):
            for value in range(OFFSET_VALUE):
                url_list = [url+f"-{month:02}-{day:02}-{value}" if value > 0 
                            else url+f"-{month:02}-{day:02}" 
                            for url in WEBSITES_LIST]
                for url in url_list:
                    if check_url(url): 
                        parse(url)
                progress_bar("Parsing...", counter, total_days*OFFSET_VALUE)
                counter += 1

    os.rename(OUTPUTFILE_PATH, OUTPUTFILE_COMPLETE_PATH)
    print(f"\n\n\033[1;32mSuccessfull complete!\033[0m --> {OUTPUTFILE_COMPLETE_PATH}")


if __name__ == "__main__":
    main()