from tuparser import (
    Config,
    ConsoleColor,
    TelegraphParser,
    YAMLOutputFile,
    compile_regex,
    run_parser,
    validate,
)


class LPParserConfig(Config):
    def parse_config(self) -> None:
        super().parse_config()
        self.exceptions = validate(
            self.config["exceptions"],
            "any_list_wn",
            default_value=[],
            exception_message="Invalid exceptions: {value}",
        ) + ["dmca@telegram.org"]
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

    async def parse(self, url: str, soup) -> None:
        website_text = list(soup.stripped_strings)
        output_data = self.extract_credentials(website_text)
        if output_data[0] != "":
            self.output_file.write_data(*output_data, url)

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
        print(
            ConsoleColor.paint_info(
                f"Output file path: {self.output_file.file_path}",
            )
        )


if __name__ == "__main__":
    output_file = YAMLOutputFile(
        {"login": {}, "password": {}, "url": {}}, "lp-parser-out"
    )
    run_parser(
        LPParser,
        config_class=LPParserConfig,
        config_path="lp-config",
        parser_args=[output_file],
    )
