from ..extensions.utils import get_time_now

LPPARSER_LOGOTYPE = r"""_      ___         ___                               
| |    | _ \  ___  | _ \  __ _   _ _   ___  ___   _ _ 
| |__  |  _/ |___| |  _/ / _` | | '_| (_-< / -_) | '_|
|____| |_|         |_|   \__,_| |_|   /__/ \___| |_|  
"""

LAUNCH_TIME = get_time_now()

SEMAPHORE_MAX_LIMIT = 100

OUTPUT_FOLDER_NAME = "parser-output"
OUTPUT_FILE_PATTERN = {"login": {}, "password": {}, "url": {}}

FULL_CHAR = "█"
HALF_CHAR = "▒"
TOTAL_PROGRESS = "[{current}/{total}]"  # [15/100]
PERCENT_PROGRESS = "[{percent:.2f}%]"  # [15.00%]
RAW_PROGRESS_BAR_LENGTH = 64

PARSING_START_MESSAGE = """Parsing has started...
Do not turn off the program until the process is completed!\n"""

ERROR_TITLE = "APPLICATION ERROR"
SUCCESS_COMPLETE_TITLE = "SUCCESSFULLY COMPLETED"

TIME_ELAPSED_TEXT = "Time elapsed: {time}"
CONFIG_FILE_ERROR_MESSAGE = "The config.yml file is incorrect"
FILE_NOT_FOUND_TEXT = "The config.yml file is missing"
INVALID_OFFSET_TEXT = "Offset value is incorrect: {offset_value} (value must be an integer and greater than 2)"
INVALID_RELEASE_DATE_TEXT = "Invalid release date: {release_date}"
INVALID_WEBSITES_TEXT = "Invalid url in websites list: {url}"
