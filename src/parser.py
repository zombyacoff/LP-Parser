import asyncio
from typing import Generator, List, Tuple

import aiohttp
from bs4 import BeautifulSoup

from .config import Config
from .constants import (
    LAUNCH_TIME,
    PARSING_START_MESSAGE,
    SEMAPHORE_MAX_LIMIT,
    SUCCESS_COMPLETE_TITLE,
    TIME_ELAPSED_TEXT,
    OUTPUT_FILE_PATH_MESSAGE,
)
from .exceptions.config import InvalidWebsiteURLError
from .extensions.progress_bar import ProgressBar
from .file_operations.output_file import OutputFile
from .utils import get_monthrange, get_time_now, paint_text


class Parser:
    def __init__(self, config: Config, output_file: OutputFile) -> None:
        self.config = config
        self.output_file = output_file
        self.bar_counter = 1

    async def _process_url(self, url: str, session: aiohttp.ClientSession) -> None:
        try:
            async with session.get(url) as page:
                ProgressBar.show(self.bar_counter, self.config.total_urls)
                self.bar_counter += 1
                if page.status != 200:
                    return
                soup = BeautifulSoup(await page.text(), "html.parser")
        except aiohttp.InvalidURL:
            raise InvalidWebsiteURLError(url=url) from None

        if not self._check_release_date(soup):
            return

        self._parse(url, soup)

    def _check_release_date(self, soup: BeautifulSoup) -> bool:
        if not self.config.release_date_bool:
            return True

        time_element = soup.select_one("time")
        release_date = (
            int(time_element.get_text("\n", strip=True)[-4:])
            if time_element
            else LAUNCH_TIME.year
        )
        return release_date in self.config.release_date

    def _parse(self, url: str, soup: BeautifulSoup) -> None:
        website_text = list(soup.stripped_strings)
        output_data = self._extract_credentials(website_text) + (url,)
        if output_data[0] != "":
            self.output_file.write_output(output_data)

    def _extract_credentials(self, website_text: List[str]) -> Tuple[str, str]:
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

    def _generate_urls(self) -> Generator[str, None, None]:
        # return [
        #     (
        #         f"{url}-{month:02}-{day:02}-{offset}"
        #         if offset > 1
        #         else f"{url}-{month:02}-{day:02}"
        #     )
        #     for month in range(1, self.config.total_months + 1)
        #     for day in range(1, get_monthrange(month) + 1)
        #     for offset in range(1, self.config.offset_value + 1)
        #     for url in self.config.websites
        # ]
        for month in range(1, self.config.total_months + 1):
            for day in range(1, get_monthrange(month) + 1):
                for offset in range(1, self.config.offset_value + 1):
                    for url in self.config.websites:
                        yield (
                            f"{url}-{month:02}-{day:02}-{offset}"
                            if offset > 1
                            else f"{url}-{month:02}-{day:02}"
                        )

    async def _semaphore_process(
        self, url: str, semaphore: asyncio.Semaphore, session: aiohttp.ClientSession
    ) -> None:
        async with semaphore:
            await self._process_url(url, session)

    def _get_complete_message(self) -> None:
        # SUCCESSFULLY COMPLETED
        # Time elapsed: 0:00:01.012345
        # --> parser-output\output_file_name.yml
        elapsed_time = get_time_now() - LAUNCH_TIME
        print(
            paint_text(SUCCESS_COMPLETE_TITLE, 32, True)
            + " "
            * (
                ProgressBar.get_length(self.config.total_urls)
                - len(SUCCESS_COMPLETE_TITLE)
            ),
            paint_text(
                f"{TIME_ELAPSED_TEXT.format(time=elapsed_time)}\n"
                f"{OUTPUT_FILE_PATH_MESSAGE.format(
                    output_file_path=self.output_file.output_file_path
                )}",
                33,
            ),
            sep="\n",
        )

    async def main(self) -> None:
        semaphore = asyncio.Semaphore(SEMAPHORE_MAX_LIMIT)
        async with aiohttp.ClientSession() as session:
            urls_generator = self._generate_urls()
            processes = [
                self._semaphore_process(url, semaphore, session)
                for url in urls_generator
            ]
            print(paint_text(PARSING_START_MESSAGE, 33))
            await asyncio.gather(*processes)

        self.output_file.complete_output()
        self._get_complete_message()
