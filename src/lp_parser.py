import asyncio
from calendar import monthrange

import aiohttp
from bs4 import BeautifulSoup

from .config import Config
from .constants import (
    INCORRECT_WEBSITES_TEXT,
    LAUNCH_TIME,
    PARSING_START_MESSAGE,
    SEMAPHORE_MAX_LIMIT,
    SUCCESS_COMPLETE_TITLE,
    TIME_ELAPSED_TEXT,
)
from .extensions import ConfigException, ProgressBar
from .output_file import OutputFile
from .utils import get_launch_time, paint_text


class LPParser:
    def __init__(self, config: Config, output_file: OutputFile) -> None:
        self.config = config
        self.output_file = output_file
        self.bar_counter = 1

    async def __process_url(self, url: str, session: aiohttp.ClientSession) -> None:
        try:
            async with session.get(url) as page:
                ProgressBar.show_progress_bar(self.bar_counter, self.config.total_urls)
                self.bar_counter += 1
                if page.status != 200:
                    return
                soup = BeautifulSoup(await page.text(), "html.parser")
        except aiohttp.InvalidURL as error:
            raise ConfigException(INCORRECT_WEBSITES_TEXT) from error
        if not self.__check_release_date(soup):
            return
        self.__parse(url, soup)

    def __check_release_date(self, soup: BeautifulSoup) -> bool:
        if not self.config.release_date_bool:
            return True
        time_element = soup.select_one("time")
        release_date = (
            int(time_element.get_text("\n", strip=True)[-4:])
            if time_element
            else LAUNCH_TIME.year
        )
        return release_date in self.config.release_date

    def __parse(self, url: str, soup: BeautifulSoup) -> None:
        website_text = list(soup.stripped_strings)
        output_data = self.__extract_credentials(website_text) + (url,)
        if output_data[0] != "":
            self.output_file.write_output(output_data)

    def __extract_credentials(self, website_text: list[str]) -> tuple[str, str]:
        login = password = ""
        for i, current in enumerate(website_text):
            email_match = self.config.login_regex.search(current)
            if email_match is None or email_match.group() in self.config.exceptions:
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
                break
        return login, password

    async def main(self) -> None:
        processes = []
        semaphore = asyncio.Semaphore(SEMAPHORE_MAX_LIMIT)
        async with aiohttp.ClientSession() as session:
            url_list = [
                (
                    f"{url}-{month:02}-{day:02}-{offset}"
                    if offset > 1
                    else f"{url}-{month:02}-{day:02}"
                )
                for month in range(1, self.config.total_months + 1)
                for day in range(1, monthrange(2020, month)[1] + 1)
                for offset in range(1, self.config.offset_value + 1)
                for url in self.config.websites
            ]
            for url in url_list:
                async with semaphore:
                    process = asyncio.create_task(self.__process_url(url, session))
                    processes.append(process)
            print(paint_text(PARSING_START_MESSAGE, 33))
            await asyncio.gather(*processes)
        self.output_file.complete_output()
        elapsed_time = get_launch_time() - LAUNCH_TIME
        print(
            paint_text(SUCCESS_COMPLETE_TITLE, 32, True) + " " * 128,
            paint_text(TIME_ELAPSED_TEXT.format(time=elapsed_time), 36),
            f"--> {self.output_file.output_file_path}",
            sep="\n",
        )
