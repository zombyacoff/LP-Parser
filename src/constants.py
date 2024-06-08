from .utils import get_time_now

LAUNCH_TIME = get_time_now()

# for Config
CONFIG_FILE_NAME = "config.yml"

# for OutputFile
OUTPUT_FOLDER_NAME = "parser-output"
OUTPUT_FILE_PATTERN = {"login": {}, "password": {}, "url": {}}

SEMAPHORE_MAX_LIMIT = 150

# parser messages
LPPARSER_LOGOTYPE = r"""_      ___         ___                               
| |    | _ \  ___  | _ \  __ _   _ _   ___  ___   _ _ 
| |__  |  _/ |___| |  _/ / _` | | '_| (_-< / -_) | '_|
|____| |_|         |_|   \__,_| |_|   /__/ \___| |_|  
"""
PARSING_START_MESSAGE = """Parsing has started...
Do not turn off the program until the process is completed!\n"""
SUCCESS_COMPLETE_TITLE = "SUCCESSFULLY COMPLETED"
TIME_ELAPSED_TEXT = "Time elapsed: {time}"
OUTPUT_FILE_PATH_MESSAGE = "Output file path: {output_file_path}"
