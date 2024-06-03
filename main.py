import asyncio
import os
import re
from datetime import datetime
from calendar import monthrange
import aiohttp
from bs4 import BeautifulSoup
import yaml


LAUNCH_TIME = datetime.now()
SEMAPHORE_MAX_LIMIT = 100
# Progress bar chars
FULL_CHAR = "█"
HALF_CHAR = "▒"


def paint_text(text: str, color_code: int, bold=False) -> str:
    return (
        f"\033[1;{color_code}m{text}\033[0m"
        if bold
        else f"\033[{color_code}m{text}\033[0m"
    )


class Config:
    def __init__(self, config_path="config/settings.yml") -> None:
        self.config_path = config_path
        self._load_settings()
        self._parse_settings()
        self.total_months = self._calculate_total_months()
        self.total_days = self._calculate_total_days()
        self.total_url = self._calculate_total_url()

    def _load_settings(self) -> None:
        try:
            with open(self.config_path) as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            raise ValueError("The settings.yml file is missing!")

    def _parse_settings(self) -> None:
        try:
            self.offset_bool = self.config["offset"]["offset"]
            self.offset_value = self._validate_offset(self.config["offset"]["value"])
            self.release_date_bool = self.config["release_date"]["release_date"]
            self.release_date = self.config["release_date"]["years"]
            self.websites_list = self.config["websites_list"]
            self.exceptions_list = self.config["exceptions_list"]
            self.login_regex = self._compile_regex(
                self.config["for_advanced_users"]["login_regex"]
            )
            self.password_regex = self._compile_regex(
                self.config["for_advanced_users"]["password_regex"]
            )
        except Exception as error:
            raise ValueError(f"The settings.yml file is incorrect: {error}")

    def _validate_offset(self, value: int) -> int:
        if not self.offset_bool:
            return 1
        if type(value) is not int and value < 2:
            raise ValueError(f"Offset value is incorrect")
        return value

    def _compile_regex(self, regex_str: str) -> re.Pattern:
        return re.compile(rf"{regex_str}")

    def _calculate_total_months(self) -> int:
        if self.release_date_bool and [LAUNCH_TIME.year] == self.release_date:
            return LAUNCH_TIME.month
        return 12

    def _calculate_total_days(self) -> int:
        if self.total_months == 12:
            return 366  # Number of days in a leap year
        return sum(
            monthrange(2020, month)[1] for month in range(1, self.total_months + 1)
        )

    def _calculate_total_url(self) -> int:
        return len(self.websites_list) * self.offset_value * self.total_days


class OutputFile:
    def __init__(self, output_file_pattern: dict, folder_name="parser-output") -> None:
        self.folder_name = folder_name
        self.launch_time_format = LAUNCH_TIME.strftime("%d-%m-%Y-%H-%M-%S")
        self.output_file_name = f"{self.launch_time_format}.yml"
        self.output_file_path = os.path.join(self.folder_name, self.output_file_name)
        self.output_data = output_file_pattern
        self.output_file_index = 1

    def _create_folder(self) -> None:
        os.makedirs(self.folder_name, exist_ok=True)

    def write_output(self, data: tuple[str, str, str]) -> None:
        for i, key in enumerate(self.output_data):
            self.output_data[key][self.output_file_index] = data[i]
        self.output_file_index += 1

    def complete_output(self) -> None:
        self._create_folder()
        with open(self.output_file_path, "w") as file:
            yaml.dump(self.output_data, file)


class LPParser:
    def __init__(self, config: Config, output_file: OutputFile) -> None:
        self.config = config
        self.output_file = output_file
        self.bar_counter = 1

    def _get_progress_bar(self) -> None:
        percent = 100 * self.bar_counter / self.config.total_url
        bar_length = round(percent) // 2
        bar = bar_length * FULL_CHAR + (50 - bar_length) * HALF_CHAR
        percent_progress = paint_text(f"[{percent:.2f}%]", 1)  # [14.43%]
        progress_status = f"[{self.bar_counter}/{self.config.total_url}]"  # [210/366]
        print(bar, percent_progress, progress_status, end="\r")
        self.bar_counter += 1

    async def _process_url(self, url: str, session: aiohttp.ClientSession) -> None:
        try:
            async with session.get(url) as page:
                self._get_progress_bar()
                if page.status != 200:
                    return
                soup = BeautifulSoup(await page.text(), "html.parser")
            if self.config.release_date_bool and not self._check_release_date(soup):
                return
            self._parse(url, soup)
        except aiohttp.InvalidURL:
            raise ValueError("Invalid websites list in config file!")

    def _check_release_date(self, soup: BeautifulSoup) -> bool:
        time_element = soup.select_one("time")
        release_date = (
            int(time_element.get_text("\n", strip=True)[-4:])
            if time_element
            else LAUNCH_TIME.year
        )
        return release_date in self.config.release_date

    def _parse(self, url: str, soup: BeautifulSoup) -> None:
        website_text = [sentence for sentence in soup.stripped_strings]
        output_data = self._extract_credentials(website_text) + (url,)
        if output_data[0] != "":
            self.output_file.write_output(output_data)

    def _extract_credentials(self, website_text: list[str]) -> tuple[str, str]:
        login = password = ""
        for i, current in enumerate(website_text):
            email_match = self.config.login_regex.search(current)
            if (
                email_match is None
                or email_match.group() in self.config.exceptions_list
            ):
                continue
            login = email_match.group()
            if ":" in login:
                data = login.split(":")
                login, password = data[0], data[-1]
                return login, password
            for k in range(1, min(4, len(website_text) - i)):
                password_match = self.config.password_regex.search(website_text[i + k])
                if password_match is None:
                    continue
                password = password_match.group()
                return login, password
        return login, password

    async def main(self) -> None:
        processes = []
        semaphore = asyncio.Semaphore(SEMAPHORE_MAX_LIMIT)
        async with aiohttp.ClientSession() as session:
            for month in range(1, self.config.total_months + 1):
                for day in range(1, monthrange(2020, month)[1] + 1):
                    for offset in range(1, self.config.offset_value + 1):
                        url_list = [
                            (
                                f"{url}-{month:02}-{day:02}-{offset}"
                                if offset > 1
                                else f"{url}-{month:02}-{day:02}"
                            )
                            for url in self.config.websites_list
                        ]
                        for url in url_list:
                            async with semaphore:
                                process = asyncio.create_task(
                                    self._process_url(url, session)
                                )
                                processes.append(process)
            print(
                f"\nParsing has started..."
                f"\n{paint_text(
                    "Do not turn off the program until the process is completed!", 
                    31)}\n"
            )
            await asyncio.gather(*processes)
        self.output_file.complete_output()
        elapsed_time = datetime.now() - LAUNCH_TIME
        print(
            f"\n\n{paint_text("Successfully completed!", 32, True)} (Time elapsed: {elapsed_time})"
            f"\n>>> {self.output_file.output_file_path}"
        )


def main() -> None:
    # fmt: off
    print(paint_text(r"""
_      ___         ___                               
| |    | _ \  ___  | _ \  __ _   _ _   ___  ___   _ _ 
| |__  |  _/ |___| |  _/ / _` | | '_| (_-< / -_) | '_|
|____| |_|         |_|   \__,_| |_|   /__/ \___| |_|  
    """, 1))
    # fmt: on
    try:
        config = Config()
        output_file = OutputFile({"login": {}, "password": {}, "url": {}})
        parser = LPParser(config, output_file)
        asyncio.run(parser.main())
    except ValueError as error:
        print(paint_text("ERROR", 31, True), error)
    except Exception as error:
        print(paint_text("UNEXPECTED ERROR", 31, True), error)


if __name__ == "__main__":
    main()
