import re
from datetime import datetime


def paint_text(text: str, color_code: int, bold=False) -> str:
    return (
        f"\033[1;{color_code}m{text}\033[0m"
        if bold
        else f"\033[{color_code}m{text}\033[0m"
    )


def get_launch_time() -> datetime:
    return datetime.now()


def compile_regex(regex: str) -> re.Pattern:
    return re.compile(regex)
