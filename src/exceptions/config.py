from dataclasses import dataclass

from .base import ApplicationException
from .messages import (
    CONFIG_FILE_ERROR_MESSAGE,
    CONFIG_NOT_FOUND_TEXT,
    INVALID_OFFSET_TEXT,
    INVALID_RELEASE_DATE_TEXT,
    INVALID_WEBSITES_TEXT,
)


class ConfigException(ApplicationException):
    """Base class for all config exceptions"""

    @property
    def message(self) -> str:
        return CONFIG_FILE_ERROR_MESSAGE


@dataclass(frozen=True, eq=False)
class ConfigNotFoundError(ConfigException):
    @property
    def message(self) -> str:
        return CONFIG_NOT_FOUND_TEXT


@dataclass(frozen=True, eq=False)
class InvalidOffsetValueError(ConfigException):
    offset_value: any

    @property
    def message(self) -> str:
        return INVALID_OFFSET_TEXT.format(offset_value=self.offset_value)


@dataclass(frozen=True, eq=False)
class InvalidReleaseDateError(ConfigException):
    release_date: any

    @property
    def message(self) -> str:
        return INVALID_RELEASE_DATE_TEXT.format(release_date=self.release_date)


@dataclass(frozen=True, eq=False)
class InvalidWebsiteURLError(ConfigException):
    url: str

    @property
    def message(self) -> str:
        return INVALID_WEBSITES_TEXT.format(url=self.url)
