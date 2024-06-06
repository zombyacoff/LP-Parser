from calendar import monthrange

import yaml

from .constants import (
    FILE_NOT_FOUND_TEXT,
    INCORRECT_OFFSET_TEXT,
    INCORRECT_RELEASE_DATE_TEXT,
    LAUNCH_TIME,
)
from .extensions import ConfigException
from .utils import compile_regex


class Config:
    def __init__(self, config_path="config/config.yml") -> None:
        self.config_path = config_path
        self.__load_config()
        self.__parse_config()
        self.__calculate_totals()

    def __load_config(self) -> None:
        try:
            with open(self.config_path) as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError as error:
            raise ConfigException(FILE_NOT_FOUND_TEXT) from error

    def __parse_config(self) -> None:
        try:
            self.offset_bool = self.config["offset"]["offset"]
            self.offset_value = self.__validate_offset(self.config["offset"]["value"])
            self.release_date_bool = self.config["release_date"]["release_date"]
            self.release_date = self.__validate_release_date(
                self.config["release_date"]["years"]
            )
            self.websites = self.config["websites"]
            self.exceptions = self.config["exceptions"]
            self.login_regex = compile_regex(
                self.config["for_advanced_users"]["login_regex"]
            )
            self.password_regex = compile_regex(
                self.config["for_advanced_users"]["password_regex"]
            )
        except (KeyError, TypeError, ConfigException) as error:
            raise ConfigException(error) from error

    def __validate_offset(self, value: int) -> int:
        if not self.offset_bool:
            return 1
        if not isinstance(value, int) or value < 2:
            raise ConfigException(INCORRECT_OFFSET_TEXT)
        return value

    def __validate_release_date(self, values: list[int]) -> list[int] | None:
        if not self.release_date_bool:
            return None
        if any(
            not isinstance(value, int) or value < 0 or value > LAUNCH_TIME.year
            for value in values
        ):
            raise ConfigException(INCORRECT_RELEASE_DATE_TEXT)
        return values

    def __calculate_totals(self) -> int:
        self.total_months = (
            LAUNCH_TIME.month
            if self.release_date_bool and self.release_date == [LAUNCH_TIME.year]
            else 12
        )
        self.total_days = (
            sum(
                monthrange(LAUNCH_TIME.year, month)[1]
                for month in range(1, self.total_months + 1)
            )
            if self.total_months != 12
            else 366
        )
        self.total_urls = len(self.websites) * self.offset_value * self.total_days
