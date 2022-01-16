from enum import Enum
from functools import reduce
from operator import or_

import Setting
from bs4 import BeautifulSoup
from script.operation_type import OperationType

from page.driver_manager import DriverManager


class Tags(Enum):
    __ENTER = {"textarea"}
    __SELECT = {"select"}
    __CLICK = Setting.TAG_CLICK
    __DICT = {
        OperationType.ENTER: __ENTER,
        OperationType.SELECT: __SELECT,
        OperationType.CLICK: __CLICK,
    }

    @classmethod
    def get_target_tags(cls, operation_type: OperationType):
        return cls.__DICT.value[operation_type]

    @classmethod
    def get_all_tags(cls):
        return set(reduce(or_, cls.__DICT.value.values())) | {"input"}


class HtmlParser:
    def __init__(self, html):
        self.__parser = BeautifulSoup(html, "html.parser")

    def find_all(self, tags):
        return self.__parser.find_all(tags)

    def select(self, query):
        return self.__parser.select(query)


class PageManager:
    def __init__(self, driver_manager: DriverManager):
        self.__driver_manager = driver_manager

    def get_elements(self):
        html = self.__driver_manager.get_page_source()
        self.__parser = HtmlParser(html)
        bs_elems = self.__parser.find_all(Tags.get_all_tags())
        return bs_elems

    def get_associated_labels(self, for_id):
        return [label.text for label in self.__parser.select("label[for='{}']".format(for_id))]
