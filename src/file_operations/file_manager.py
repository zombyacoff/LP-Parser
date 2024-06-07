import os

import yaml


class FileManager:
    @staticmethod
    def create_folder(folder_path: str) -> None:
        os.makedirs(folder_path, exist_ok=True)

    @staticmethod
    def join_paths(paths: tuple[str]) -> str:
        return os.path.join(*paths)

    @staticmethod
    def safe_yaml_file(file_path: str) -> dict:
        with open(file_path) as file:
            return yaml.safe_load(file)

    @staticmethod
    def damp_yaml_file(file_path: str, data: dict) -> None:
        with open(file_path, "w") as file:
            yaml.dump(data, file)
