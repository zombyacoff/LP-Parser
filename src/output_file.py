import os

import yaml

from .constants import LAUNCH_TIME, OUTPUT_FILE_PATTERN, OUTPUT_FOLDER_NAME


class OutputFile:
    def __init__(self) -> None:
        self.output_data = OUTPUT_FILE_PATTERN
        self.launch_time_format = LAUNCH_TIME.strftime("%d-%m-%Y-%H-%M-%S")
        self.output_file_name = f"{self.launch_time_format}.yml"
        self.output_file_path = os.path.join(OUTPUT_FOLDER_NAME, self.output_file_name)
        self.output_file_index = 1

    def __create_folder(self) -> None:
        os.makedirs(OUTPUT_FOLDER_NAME, exist_ok=True)

    def write_output(self, data: tuple) -> None:
        for i, key in enumerate(self.output_data):
            self.output_data[key][self.output_file_index] = data[i]
        self.output_file_index += 1

    def complete_output(self) -> None:
        self.__create_folder()
        with open(self.output_file_path, "w") as file:
            yaml.dump(self.output_data, file)
