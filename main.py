import asyncio

from src.config import Config
from src.constants import CONFIG_FILE_ERROR_MESSAGE, LPPARSER_LOGOTYPE
from src.extensions import ConfigException
from src.lp_parser import LPParser
from src.output_file import OutputFile
from src.utils import paint_text

if __name__ == "__main__":
    print(LPPARSER_LOGOTYPE)
    try:
        config = Config()
        output_file = OutputFile()
        parser = LPParser(config, output_file)
        asyncio.run(parser.main())
    except ConfigException as error:
        print(f"{paint_text("CONFIG ERROR", 31)}\n--> {CONFIG_FILE_ERROR_MESSAGE.format(error=error)}")
