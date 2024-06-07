import os

import yaml


class FileManager:
    @staticmethod
    def create_folder(folder_path: str) -> None:
        """Create a folder in main directory"""
        os.makedirs(folder_path, exist_ok=True)

    @staticmethod
    def join_paths(*paths: str) -> str:
        """Join paths into one string"""
        return os.path.join(*paths)

    @staticmethod
    def safe_yaml_file(file_path: str) -> dict:
        """Safely load yaml file"""
        with open(file_path, encoding="utf-8") as file:
            return yaml.safe_load(file)

    @staticmethod
    def dump_yaml_file(file_path: str, data: dict) -> None:
        """Dump yaml file"""
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.dump(data, file)
