import asyncio

from src.config.config import Config
from src.constants.constants import LPPARSER_LOGOTYPE
from src.exceptions.base import ApplicationException
from src.exceptions.config import (
    ConfigException,
    ConfigNotFoundError,
    IncorrectOffsetError,
    IncorrectReleaseDateError,
    IncorrectWebsitesError,
)
from src.file_operations.output_file import OutputFile
from src.parser import Parser

if __name__ == "__main__":
    print(LPPARSER_LOGOTYPE)
    try:
        config = Config()
        output_file = OutputFile()
        parser = Parser(config=config, output_file=output_file)
        asyncio.run(parser.main())
    except (
        ConfigException,
        ConfigNotFoundError,
        IncorrectOffsetError,
        IncorrectReleaseDateError,
        IncorrectWebsitesError,
    ) as e:
        ApplicationException.get_error_message(e)
