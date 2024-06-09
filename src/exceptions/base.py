from ..utils import ConsoleColor
from .messages import ERROR_TITLE


class ApplicationException(Exception):
    """Base class for all application exceptions"""

    @staticmethod
    def get_error_message(exception: "ApplicationException") -> str:
        print(
            ConsoleColor.paint_error(ERROR_TITLE),
            exception.message,
            sep="\n",
        )
