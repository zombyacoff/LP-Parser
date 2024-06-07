from dataclasses import dataclass

from ..constants.constants import LAUNCH_TIME, OUTPUT_FILE_PATTERN, OUTPUT_FOLDER_NAME
from .file_manager import FileManager


@dataclass
class OutputFile:
    output_data = OUTPUT_FILE_PATTERN
    launch_time_format = LAUNCH_TIME.strftime("%d-%m-%Y-%H-%M-%S")
    output_file_name = f"{launch_time_format}.yml"
    output_file_path = FileManager.join_paths((OUTPUT_FOLDER_NAME, output_file_name))
    output_file_index = 1

    def write_output(self, data: tuple) -> None:
        for i, key in enumerate(self.output_data):
            self.output_data[key][self.output_file_index] = data[i]
        self.output_file_index += 1

    def complete_output(self) -> None:
        FileManager.create_folder(OUTPUT_FOLDER_NAME)
        FileManager.dump_yaml_file(self.output_file_path, self.output_data)
