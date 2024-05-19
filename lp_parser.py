import os
import yaml
import re
import logging
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange


class Settings:
    """
    Initializes settings based on a given 
    launch time and optional file name.
    Loads settings from a YAML file and parses them.
    Calculates the year range based on the 
    launch time and release date settings.
    """
    def __init__(
        self, 
        launch_time: datetime, 
        file_name="settings.yml"
    ):
        self.__load_settings(file_name)
        self.__parse_settings()
        self.year_range = self.__year_range(launch_time)

    def __load_settings(self, file_name):
        with open(file_name) as file:
            self.settings = yaml.safe_load(file)

    def __parse_settings(self):
        self.offset_bool = self.settings["offset"]["offset"]
        self.offset = self.settings["offset"]["value"] if self.offset_bool else 1
        self.release_date_bool = self.settings["release_date"]["release_date"]
        self.release_date = self.settings["release_date"]["years"]
        self.websites_list = self.settings["websites_list"]
        self.exceptions_list = self.settings["exceptions_list"]
        self.login_regex = re.compile(rf"{self.settings["for_advanced_users"]["login_regex"]}")
        self.password_regex = re.compile(rf"{self.settings["for_advanced_users"]["password_regex"]}")

    def __year_range(self, launch_time):
        if (self.release_date_bool
            and len(self.release_date) == 1
            and launch_time in self.release_date):
            return launch_time.month
        return 12
    

class OutputFile:
    """
    Class to handle output file operations including 
    creating folders, writing output data, 
    and finalizing the output file.
    """
    def __init__ (
        self, 
        launch_time: datetime, 
        output_file_pattern: dict, 
        folder_name: str
    ):
        self.folder_name = folder_name
        self.launch_time_format = launch_time.strftime("%d-%m-%Y-%H-%M-%S")
        self.output_file_path = f"{self.folder_name}/{self.launch_time_format}.yml"
        self.output_file_complete_path = f"{self.folder_name}/{self.launch_time_format}-complete.yml"
        self.output_file_pattern = output_file_pattern
        self.index = 1
        self.__create_folder()

    def __create_folder(self):
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
        with open(self.output_file_path, "w") as file:
            yaml.dump(self.output_file_pattern, file)
    
    def write_output(self, data: list[str]):
        with open(self.output_file_path, "r") as file:
            output_data = yaml.safe_load(file)
        for i, key in enumerate(output_data):
            output_data[key][self.index] = data[i]
        with open(self.output_file_path, "w") as file:
            yaml.dump(output_data, file)
        self.index += 1

    def finalize_output(self):
        os.rename(self.output_file_path, self.output_file_complete_path)
    

class LPParser:
    """
    Asynchronous class for parsing URLs 
    based on settings and writing output data.
    This class includes methods for processing URLs, 
    parsing website text to extract login and password information,
    and running the main asynchronous 
    process to parse multiple URLs concurrently.
    """
    def __init__(self, settings, output_file):
        self.settings = settings
        self.output_file = output_file

    async def process_url(self, url: str):
        async with aiohttp.ClientSession() as session:
            page = await session.get(url)
        if page.status != 200:
            return
        
        soup = BeautifulSoup(await page.text(), "html.parser")
        if self.settings.release_date_bool:
            time_element = soup.select_one("time")
            release_date = int(time_element.get_text("\n", strip=True)[-4:]) if time_element else 2024
            if release_date in self.settings.release_date:
                self.parse(url, soup)        
        else: self.parse(url, soup)

    def parse(self, url: str, soup: BeautifulSoup):
        website_text = [sentence for sentence in soup.stripped_strings]
        login = ""
        password = ""

        for i, text in enumerate(website_text):
            email_match = self.settings.login_regex.findall(text)
            if email_match and email_match[0] not in self.settings.exceptions_list: 
                login = email_match[0]
                if ":" in login:
                    data = login.split(":")
                    login = data[0]
                    password = data[1]
                    break
                if i < len(website_text)-4:
                    for k in range(1, 4):
                        password_match = self.settings.password_regex.findall(website_text[i+k])
                        if password_match: 
                            password = password_match[0]
                            break

        parsed_data = [login, password]
        parsed_data.append(url)
        if login != "": 
            self.output_file.write_output(parsed_data)

    async def main(self):
        processes = []  
        for month in range(1, self.settings.year_range+1):
            for day in range(1, monthrange(2020, month)[1]+1):
                for value in range(self.settings.offset):
                    url_list = [url+f"-{month:02}-{day:02}-{value}" if value > 0 
                                else url+f"-{month:02}-{day:02}" 
                                for url in self.settings.websites_list]
                    for url in url_list:
                        process = asyncio.create_task(self.process_url(url))
                        processes.append(process)
                        
        await asyncio.gather(*processes)


def main():
    logging.basicConfig(level=logging.INFO)
    launch_time = datetime.now()

    try:
        settings = Settings(launch_time)
        output_file = OutputFile(
            launch_time, 
            {
                "login": {},
                "password": {},
                "url": {}
            },
            "parser-output"
        )
        
        logging.info("\rParsing...")
        lpparser = LPParser(settings, output_file)
        asyncio.run(lpparser.main())
        output_file.finalize_output()
        logging.info(f"\rSuccessfully completed! (Time elapsed: {datetime.now() - launch_time})\n>>> {output_file.output_file_complete_path}")
    
    except Exception as error:
        logging.error(error)


if __name__ == "__main__":
    main()
