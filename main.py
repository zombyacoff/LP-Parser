import aiohttp
from tuparser.config import Config
from tuparser.file_operations.output_file import YAMLOutputFile
from tuparser.parser import TelegraphParser, run_parser
from tuparser.utils import ConsoleColor, compile_regex


class LPParserConfig(Config):
    def parse_config(self) -> None:
        super().parse_config()

        self.exceptions = self.config["exceptions"] + ["dmca@telegram.org"]
        self.login_regex = compile_regex(
            self.config["for_advanced_users"]["login_regex"]
        )
        self.password_regex = compile_regex(
            self.config["for_advanced_users"]["password_regex"]
        )


class LPParser(TelegraphParser):
    def __init__(self, config: Config, output_file: YAMLOutputFile) -> None:
        super().__init__(config)
        self.output_file = output_file

    async def process_url(
        self, url: str, session: aiohttp.ClientSession
    ) -> None:
        soup = await super().process_url(url, session)
        # return if url is not valid
        if soup is None:
            return

        website_text = list(soup.stripped_strings)
        output_data = self.extract_credentials(website_text) + (url,)
        if output_data[0] != "":
            self.output_file.write_output(output_data)

    def extract_credentials(self, website_text: list[str]) -> tuple[str, str]:
        login = password = ""

        for i, current in enumerate(website_text):
            email_match = self.config.login_regex.search(current)
            if (
                email_match is None
                or email_match.group() in self.config.exceptions
            ):
                continue
            login = email_match.group()
            if ":" in login:
                data = login.split(":")
                login, password = data[0], data[-1]
                return login, password
            for k in range(1, min(4, len(website_text) - i)):
                password_match = self.config.password_regex.search(
                    website_text[i + k]
                )
                if password_match is None:
                    continue
                password = password_match.group()
                break

        return login, password

    def get_complete_message(self) -> None:
        super().get_complete_message()
        # Output file path: parser-output\output_file_name.yml
        print(
            ConsoleColor.paint_info(
                f"Output file path: parser-output/{self.output_file.output_file_name}",
            )
        )

    async def main(self) -> None:
        await super().main()
        self.output_file.complete_output()


if __name__ == "__main__":
    output_file = YAMLOutputFile({"login": {}, "password": {}, "url": {}})
    run_parser(
        config_class=LPParserConfig,
        parser_class=LPParser,
        parser_args=(output_file,),
    )
