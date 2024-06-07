from ..constants.constants import ERROR_TITLE
from ..extensions.utils import paint_text


class ApplicationException(Exception):
    """Base class for all application exceptions"""

    @staticmethod
    def get_error_message(exception: Exception) -> str:
        print(
            paint_text(ERROR_TITLE, 31, True),
            exception.message,
            sep="\n",
        )
