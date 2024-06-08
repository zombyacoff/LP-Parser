import re
from calendar import monthrange
from datetime import datetime

from termcolor import colored


def get_time_now() -> datetime:
    """Returns the current time as a datetime object"""
    return datetime.now()


def get_monthrange(month: int) -> int:
    """Returns the number of days in a given month"""
    return monthrange(2020, month)[1]


def compile_regex(regex: str) -> re.Pattern:
    """Compiles a regex and returns a re.Pattern object"""
    return re.compile(regex)


class ConsoleColor:
    @staticmethod
    def paint_success(text: str) -> str:
        """Paints the given text in bold green"""
        return colored(text, "green", attrs=["bold"])

    @staticmethod
    def paint_error(text: str) -> str:
        """Paints the given text in bold red"""
        return colored(text, "red", attrs=["bold"])

    @staticmethod
    def paint_info(text: str) -> str:
        """Paints the given text in yellow"""
        return colored(text, "yellow")
