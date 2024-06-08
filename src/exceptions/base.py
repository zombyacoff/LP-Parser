from ..constants import RED
from ..utils import paint_text
from .messages import ERROR_TITLE


class ApplicationException(Exception):
    """Base class for all application exceptions"""

    @staticmethod
    def get_error_message(exception: Exception) -> str:
        print(
            paint_text(ERROR_TITLE, RED, True),
            exception.message,
            sep="\n",
        )
