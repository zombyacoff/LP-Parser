import re
from calendar import monthrange
from datetime import datetime


class ConfigException(Exception):
    pass


def paint_text(text: str, color_code: int, bold=False) -> str:
    return (
        f"\033[1;{color_code}m{text}\033[0m"
        if bold
        else f"\033[{color_code}m{text}\033[0m"
    )


def get_launch_time() -> datetime:
    return datetime.now()


def get_monthrange(month: int) -> int:
    return monthrange(2020, month)[1]


def compile_regex(regex: str) -> re.Pattern:
    return re.compile(regex)
