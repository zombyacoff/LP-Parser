import asyncio
import os
import re
from datetime import datetime
from calendar import monthrange
import aiohttp
from bs4 import BeautifulSoup
import yaml


LAUNCH_TIME = datetime.now()


class Config:
    def __init__(
        self, config_path="config/settings.yml"
) -> None:
        self.config_path = config_path
        self._load_settings()
        self._parse_settings()
        self.year_range = self._calculate_year_range()

    def _load_settings(self) -> None:
        with open(self.config_path) as file:
            self.config = yaml.safe_load(file)

    def _parse_settings(self) -> None:
        self.offset_bool = self.config["offset"]["offset"]
        self.offset = self.config["offset"]["value"] if self.offset_bool else 1
        self.release_date_bool = self.config["release_date"]["release_date"]
        self.release_date = self.config["release_date"]["years"]
        self.websites_list = self.config["websites_list"]
        self.exceptions_list = self.config["exceptions_list"]
        self.login_regex = self._2regex(self.config["for_advanced_users"]["login_regex"])
        self.password_regex = self._2regex(self.config["for_advanced_users"]["password_regex"])

    def _2regex(self, regex_str) -> re.Pattern:
        return re.compile(rf"{regex_str}")

    def _calculate_year_range(self) -> int:
        if (self.release_date_bool
            and len(self.release_date) == 1
            and LAUNCH_TIME.year in self.release_date):
            return LAUNCH_TIME.month
        return 12
    

class OutputFile:
    def __init__(
        self, output_file_pattern: dict, folder_name="parser-output"
) -> None:
        self.folder_name = folder_name
        self.launch_time_format = LAUNCH_TIME.strftime("%d-%m-%Y-%H-%M-%S")
        self.output_file_name = f"{self.launch_time_format}.yml"
        self.output_file_path = os.path.join(self.folder_name, self.output_file_name)
        self.output_data = output_file_pattern
        self.index = 1
        self._create_folder()

    def _create_folder(self) -> None:
        os.makedirs(self.folder_name, exist_ok=True)

    def write_output(self, data: list[str]) -> None:
        for i, key in enumerate(self.output_data):   
            self.output_data[key][self.index] = data[i]
        self.index += 1

    def complete_output(self) -> None:
        with open(self.output_file_path, "w") as file:
            yaml.dump(self.output_data, file)


class LPParser:
    def __init__(
        self, config: Config, output_file: OutputFile
) -> None:
        self.config = config
        self.output_file = output_file

    async def _process_url(
        self, url: str, session: aiohttp.ClientSession
) -> None:
        """
        Fetches and parses a URL; 
        skips processing if status isn't 200 or release date is irrelevant.
        """
        try:
            page = await session.get(url)
        except aiohttp.InvalidURL:
            raise ValueError("Invalid websites list in config file")
        if page.status != 200:
            return   
        soup = BeautifulSoup(await page.text(), "html.parser")
        if self.config.release_date_bool:
            if self._check_release_date(soup):
                return
        self._parse(url, soup)

    def _check_release_date(self, soup: BeautifulSoup) -> None:
        """ 
        Checks if the release date from 'time' 
        element is outside the specified config years
        """
        time_element = soup.select_one("time")
        release_date = (int(time_element.get_text("\n", strip=True)[-4:]) if time_element
                         else LAUNCH_TIME.year)
        return not (release_date in self.config.release_date)

    def _parse(
        self, url: str, soup: BeautifulSoup
) -> None:
        """ Parse soup to extract and write credentials if found """
        website_text = [sentence for sentence in soup.stripped_strings]
        login, password = self._extract_credentials(website_text)
        output_data = login, password, url
        if login: self._write_output(output_data)

    def _extract_credentials(
        self, website_text: list[str], login="", password=""
) -> tuple:
        """ Extracts credentials from website text """
        for i, current in enumerate(website_text):
            email_match = self.config.login_regex.search(current)
            if email_match and email_match.group() not in self.config.exceptions_list: 
                login = email_match.group()
                if ":" in login:
                    data = login.split(":")
                    login, password = data[0], data[-1]
                    return login, password
                for k in range(1, min(4, len(website_text) - i)):
                    password_match = self.config.password_regex.search(website_text[i+k])
                    if password_match:
                        password = password_match.group()
                        return login, password
        return login, password
    
    def _write_output(self, data: tuple) -> None:
        """ Writes output data """
        self.output_file.write_output(data)

    async def main(self) -> str:
        """ Main processing function of the program """
        print("Parsing has started...")
        processes = []  
        async with aiohttp.ClientSession() as session:
            for month in range(1, self.config.year_range+1):
                for day in range(1, monthrange(2020, month)[1]+1):
                    for value in range(self.config.offset):
                        url_list = [f"{url}-{month:02}-{day:02}-{value+1}" if value > 0 
                                    else f"{url}-{month:02}-{day:02}" 
                                    for url in self.config.websites_list]
                        for url in url_list:
                            process = asyncio.create_task(self._process_url(url, session))
                            processes.append(process)
            try:                  
                await asyncio.gather(*processes)
            except ValueError as error:
                return f"ERROR: {error}"
        self.output_file.complete_output()
        elapsed_time = datetime.now() - LAUNCH_TIME
        return f"Successfully completed! (Time elapsed: {elapsed_time})\
            \n>>> {self.output_file.output_file_path}"


def main():
    config = Config()
    output_file = OutputFile(
        {
            "login": {},
            "password": {},
            "url": {}
        }
    )
    parser = LPParser(config, output_file)
    # Start the parsing process
    print(asyncio.run(parser.main()))


if __name__ == "__main__":
    main()
