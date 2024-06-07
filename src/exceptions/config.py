from dataclasses import dataclass

from ..constants import (
    CONFIG_FILE_ERROR_MESSAGE,
    FILE_NOT_FOUND_TEXT,
    INVALID_OFFSET_TEXT,
    INVALID_RELEASE_DATE_TEXT,
    INVALID_WEBSITES_TEXT,
)
from .base import ApplicationException


class ConfigException(ApplicationException):
    """Base class for all config exceptions"""

    @property
    def message(self) -> str:
        return CONFIG_FILE_ERROR_MESSAGE


class ConfigNotFoundError(ConfigException):
    @property
    def message(self) -> str:
        return FILE_NOT_FOUND_TEXT


@dataclass
class InvalidOffsetValueError(ConfigException):
    offset_value: any

    @property
    def message(self) -> str:
        return INVALID_OFFSET_TEXT.format(offset_value=self.offset_value)


@dataclass
class InvalidReleaseDateError(ConfigException):
    release_date: any

    @property
    def message(self) -> str:
        return INVALID_RELEASE_DATE_TEXT.format(release_date=self.release_date)


@dataclass
class InvalidWebsiteURLError(ConfigException):
    url: any

    @property
    def message(self) -> str:
        return INVALID_WEBSITES_TEXT.format(url=self.url)
