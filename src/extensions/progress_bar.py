from ..utils import paint_text
from .constants import (
    FULL_CHAR,
    HALF_CHAR,
    PERCENT_PROGRESS,
    RAW_PROGRESS_BAR_LENGTH,
    TOTAL_PROGRESS,
)


class ProgressBar:
    @staticmethod
    def show(current: int, total: int) -> None:
        percent = 100 * current / total
        current_bar_length = round(percent) // 2
        bar = current_bar_length * FULL_CHAR + (50 - current_bar_length) * HALF_CHAR
        print(
            bar,
            TOTAL_PROGRESS.format(current=current, total=total),
            paint_text(PERCENT_PROGRESS.format(percent=percent), 1),
            end="\r",
        )

    @staticmethod
    def get_length(total: int) -> int:
        return RAW_PROGRESS_BAR_LENGTH + len(str(total)) * 2
