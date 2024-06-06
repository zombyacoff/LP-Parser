from .utils import get_launch_time

LPPARSER_LOGOTYPE = r"""
_      ___         ___                               
| |    | _ \  ___  | _ \  __ _   _ _   ___  ___   _ _ 
| |__  |  _/ |___| |  _/ / _` | | '_| (_-< / -_) | '_|
|____| |_|         |_|   \__,_| |_|   /__/ \___| |_|  """

LAUNCH_TIME = get_launch_time()

SEMAPHORE_MAX_LIMIT = 100

OUTPUT_FOLDER_NAME = "parser-output"
OUTPUT_FILE_PATTERN = {"login": {}, "password": {}, "url": {}}

FULL_CHAR = "█"
HALF_CHAR = "▒"
TOTAL_PROGRESS = "[{current}/{total}]"  # [15/100]
PERCENT_PROGRESS = "[{percent:.2f}%]"  # [15.00%]

CONFIG_FILE_ERROR_MESSAGE = "The config.yml file is incorrect: {error}"
FILE_NOT_FOUND_MESSAGE = "The config.yml file is missing!"
INCORRECT_OFFSET_MESSAGE = (
    "Offset value is incorrect (value must be an integer and greater than 2)"
)
INCORRECT_RELEASE_DATE_MESSAGE = "Release date list is incorrect"
INCORRECT_WEBSITES_MESSAGE = "Websites is incorrect"
PARSING_START_MESSAGE = """\nParsing has started...
Do not turn off the program until the process is completed!\n"""
SUCCESS_COMPLETE_MESSAGE = """\n\nSuccessfully completed! (Time elapsed: {elapsed_time})
>>> {output_file_path}"""
