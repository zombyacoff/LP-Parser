import asyncio

from src.config.config import Config
from src.constants.constants import LPPARSER_LOGOTYPE
from src.exceptions.base import ApplicationException
from src.exceptions.config import (
    ConfigException,
    ConfigNotFoundError,
    InvalidOffsetValueError,
    InvalidReleaseDateError,
    InvalidWebsiteURLError,
)
from src.file_operations.output_file import OutputFile
from src.parser import Parser


def main() -> None:
    print(LPPARSER_LOGOTYPE)
    try:
        config = Config()
        output_file = OutputFile()
        parser = Parser(config=config, output_file=output_file)
        asyncio.run(parser.main())
    except (
        ConfigException,
        ConfigNotFoundError,
        InvalidOffsetValueError,
        InvalidReleaseDateError,
        InvalidWebsiteURLError,
    ) as e:
        ApplicationException.get_error_message(e)


if __name__ == "__main__":
    main()
