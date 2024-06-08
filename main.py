import asyncio

from src.config import Config
from src.constants import (
    CONFIG_FILE_NAME,
    LPPARSER_LOGOTYPE,
    OUTPUT_FILE_PATTERN,
    OUTPUT_FOLDER_NAME,
)
from src.exceptions.base import ApplicationException
from src.exceptions.config import (
    ConfigNotFoundError,
    InvalidConfigError,
    InvalidOffsetValueError,
    InvalidReleaseDateError,
    InvalidWebsiteURLError,
)
from src.file_operations.output_file import OutputFile
from src.parser import Parser


def main() -> None:
    print(LPPARSER_LOGOTYPE)
    try:
        config = Config(CONFIG_FILE_NAME)
        output_file = OutputFile(OUTPUT_FILE_PATTERN, OUTPUT_FOLDER_NAME)
        parser = Parser(config, output_file)
        asyncio.run(parser.main())
    except (
        InvalidConfigError,
        ConfigNotFoundError,
        InvalidOffsetValueError,
        InvalidReleaseDateError,
        InvalidWebsiteURLError,
    ) as e:
        ApplicationException.get_error_message(e)


if __name__ == "__main__":
    main()
