import asyncio
import os
import re
from datetime import datetime
from calendar import monthrange
import aiohttp
from bs4 import BeautifulSoup
import yaml


class Config:
    def __init__(
        self, 
        launch_time: datetime, 
        config_path="config/settings.yml"
    ):
        self._load_settings(config_path)
        self._parse_settings()
        self.year_range = self._calculate_year_range(launch_time)

    def _load_settings(self, config_path):
        with open(config_path) as file:
            self.config = yaml.safe_load(file)

    def _parse_settings(self):
        self.offset_bool = self.config["offset"]["offset"]
        self.offset = self.config["offset"]["value"] if self.offset_bool else 1
        self.release_date_bool = self.config["release_date"]["release_date"]
        self.release_date = self.config["release_date"]["years"]
        self.websites_list = self.config["websites_list"]
        self.exceptions_list = self.config["exceptions_list"]
        self.login_regex = re.compile(rf"{self.config["for_advanced_users"]["login_regex"]}")
        self.password_regex = re.compile(rf"{self.config["for_advanced_users"]["password_regex"]}")

    def _calculate_year_range(self, launch_time):
        if (self.release_date_bool
            and len(self.release_date) == 1
            and launch_time in self.release_date):
            return launch_time.month
        return 12
    

class OutputFile:
    def __init__(
        self, 
        launch_time: datetime, 
        output_file_pattern: dict, 
        folder_name="parser-output"
    ):
        self.folder_name = folder_name
        self.launch_time_format = launch_time.strftime("%d-%m-%Y-%H-%M-%S")
        self.output_file_name = f"{self.launch_time_format}.yml"
        self.output_file_path = os.path.join(self.folder_name, self.output_file_name)
        self.output_data = output_file_pattern
        self.index = 1
        self._create_folder()

    def _create_folder(self):
        os.makedirs(self.folder_name, exist_ok=True)

    def write_output(self, data: list[str]):
        for i, key in enumerate(self.output_data):   
            self.output_data[key][self.index] = data[i]
        self.index += 1

    def complete_output(self):
        with open(self.output_file_path, "w") as file:
            yaml.dump(self.output_data, file)

    
class LPParser:
    def __init__(
        self, 
        config: Config, 
        output_file: OutputFile
    ):
        self.config = config
        self.output_file = output_file

    async def _process_url(
        self, 
        url: str,
        session: aiohttp.ClientSession
    ):
        page = await session.get(url)
        if page.status != 200:
            return
        
        soup = BeautifulSoup(await page.text(), "html.parser")
        if self.config.release_date_bool:
            time_element = soup.select_one("time")
            release_date = int(time_element.get_text("\n", strip=True)[-4:]) if time_element else 2024
            if release_date in self.config.release_date:
                self._parse(url, soup)        
        else: 
            self._parse(url, soup)

    def _parse(
        self, 
        url: str, 
        soup: BeautifulSoup
    ):
        website_text = [sentence for sentence in soup.stripped_strings]
        login = password = ""

        for i, text in enumerate(website_text):
            email_match = self.config.login_regex.search(text)
            if email_match and email_match.group() not in self.config.exceptions_list: 
                login = email_match.group()
                if ":" in login:
                    data = login.split(":")
                    login = data[0]; password = data[1]
                    break
                if i < len(website_text)-4:
                    for k in range(1, 4):
                        password_match = self.config.password_regex.search(website_text[i+k])
                        if password_match: 
                            password = password_match.group()
                            break

        parsed_data = [login, password]
        parsed_data.append(url)
        if login != "": 
            self.output_file.write_output(parsed_data)

    async def main(self):
        async with aiohttp.ClientSession() as session:
            processes = []  
            for month in range(1, self.config.year_range+1):
                for day in range(1, monthrange(2020, month)[1]+1):
                    for value in range(self.config.offset):
                        url_list = [url+f"-{month:02}-{day:02}-{value+1}" if value > 0 
                                    else url+f"-{month:02}-{day:02}" 
                                    for url in self.config.websites_list]
                        for url in url_list:
                            process = asyncio.create_task(self._process_url(url, session))
                            processes.append(process)                     
            await asyncio.gather(*processes)
        self.output_file.complete_output()


def main():
    launch_time = datetime.now()
    config = Config(launch_time)
    output_file = OutputFile(
        launch_time, 
        {
            "login": {},
            "password": {},
            "url": {}
        }
    )
    parser = LPParser(config, output_file)

    print("Parsing...")
    asyncio.run(parser.main())
    elapsed_time = datetime.now() - launch_time
    print(f"Successfully completed! (Time elapsed: {elapsed_time})\n>>> {output_file.output_file_path}")


if __name__ == "__main__":
    main()
