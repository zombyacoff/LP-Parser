from .constants import FULL_CHAR, HALF_CHAR, PERCENT_PROGRESS, TOTAL_PROGRESS


class ProgressBar:
    """
    Progress bar example:
    █████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ [27/100] [27.00%]
    """

    @staticmethod
    def show(current: int, total: int) -> None:
        percent = 100 * current / total
        current_bar_length = round(percent) // 2
        bar = current_bar_length * FULL_CHAR + (50 - current_bar_length) * HALF_CHAR
        print(
            bar,
            TOTAL_PROGRESS.format(current=current, total=total),
            PERCENT_PROGRESS.format(percent=percent),
            end="\r",
        )

    @staticmethod
    def get_length(total: int) -> int:
        return 64 + len(str(total)) * 2
