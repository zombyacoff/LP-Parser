import os

from .constants import LAUNCH_TIME, OUTPUT_FILE_PATTERN, OUTPUT_FOLDER_NAME
from .utils import FileManager


class OutputFile:
    def __init__(self) -> None:
        self.output_data = OUTPUT_FILE_PATTERN
        self.launch_time_format = LAUNCH_TIME.strftime("%d-%m-%Y-%H-%M-%S")
        self.output_file_name = f"{self.launch_time_format}.yml"
        self.output_file_path = os.path.join(OUTPUT_FOLDER_NAME, self.output_file_name)
        self.output_file_index = 1

    def write_output(self, data: tuple) -> None:
        for i, key in enumerate(self.output_data):
            self.output_data[key][self.output_file_index] = data[i]
        self.output_file_index += 1

    def complete_output(self) -> None:
        FileManager.create_folder(OUTPUT_FOLDER_NAME)
        FileManager.damp_yaml_file(self.output_file_path, self.output_data)
