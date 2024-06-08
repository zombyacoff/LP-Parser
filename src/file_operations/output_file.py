from dataclasses import dataclass

from ..constants import LAUNCH_TIME
from .file_manager import FileManager


@dataclass(eq=False)
class OutputFile:
    output_data: dict[str, dict]
    output_folder_name: str
    launch_time_format: str = LAUNCH_TIME.strftime("%d-%m-%Y-%H-%M-%S")
    output_file_name: str = f"{launch_time_format}.yml"
    output_file_index: int = 1

    def __post_init__(self) -> None:
        self.output_file_path: str = FileManager.join_paths(
            self.output_folder_name, self.output_file_name
        )

    def write_output(self, data: tuple[any]) -> None:
        for i, key in enumerate(self.output_data):
            self.output_data[key][self.output_file_index] = data[i]
        self.output_file_index += 1

    def complete_output(self) -> None:
        FileManager.create_folder(self.output_folder_name)
        FileManager.dump_yaml_file(self.output_file_path, self.output_data)
