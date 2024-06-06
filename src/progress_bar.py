from .constants import FULL_CHAR, HALF_CHAR, PERCENT_PROGRESS, TOTAL_PROGRESS


class ProgressBar:
    """
    Progress bar example:
    █████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ [27/100] [27.00%]
    """

    @staticmethod
    def show_progress_bar(current: int, total: int) -> None:
        percent = 100 * current / total
        bar_length = round(percent) // 2
        bar = bar_length * FULL_CHAR + (50 - bar_length) * HALF_CHAR
        print(
            bar,
            TOTAL_PROGRESS.format(current=current, total=total),
            PERCENT_PROGRESS.format(percent=percent),
            end="\r",
        )
