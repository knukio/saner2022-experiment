from enum import Enum


class LocatorType(Enum):
    ID = "id"
    NAME = "name"
    LINK_TEXT = "partial_link_text"
    XPATH = "xpath"


class Locator:
    def __init__(self, locator_type: LocatorType, value):
        self.__locator_type = locator_type
        self.__value = value

    @property
    def locator_type(self):
        return self.__locator_type

    @property
    def value(self):
        return self.__value
