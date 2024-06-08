import re
from calendar import monthrange
from datetime import datetime


def paint_text(text: str, color_code: int, bold=False) -> str:
    """Paint a text in console"""
    return (
        f"\033[1;{color_code}m{text}\033[0m"
        if bold
        else f"\033[{color_code}m{text}\033[0m"
    )


def get_time_now() -> datetime:
    """Returns the current time as a datetime object"""
    return datetime.now()


def get_monthrange(month: int) -> int:
    """Returns the number of days in a given month"""
    return monthrange(2020, month)[1]


def compile_regex(regex: str) -> re.Pattern:
    """Compiles a regex and returns a re.Pattern object"""
    return re.compile(regex)
