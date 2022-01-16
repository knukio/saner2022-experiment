from collections import defaultdict
from typing import DefaultDict, List

import Setting
from calculator import VectorCalculator
from script.operation_type import OperationType
from util.word_util import WordUtil

from page.element import Element
from page.page_manager import PageManager, Tags


class ElementContainer:
    def __init__(self, page_manager: PageManager):
        self.__page_manager = page_manager

    @property
    def elems(self):
        return self.__elems

    def get_elems_of(self, operationType: OperationType) -> List[Element]:
        return self.__elem_dict[operationType]

    def extract_element(self):
        self.__elems = []
        self.__bs_elems = self.__page_manager.get_elements()
        for i, bs_elem in enumerate(self.__bs_elems):
            if self.__is_invisible(bs_elem):
                continue
            attr_words = self.__extract_attr_words(bs_elem)
            if attr_words == []:
                continue
            text_words = self.__extract_text_words(bs_elem)
            elem: Element = Element(bs_elem, i, attr_words, text_words)
            self.__elems.append(elem)
        self.__create_elem_dict()

    def append_vector(self, vector_calculator: VectorCalculator):
        for elem in self.elems:
            elem.attr_vector = vector_calculator.get_elem_vector(elem)
            elem.text_vector = vector_calculator.get_text_vector(elem)

    def __create_elem_dict(self):
        # clicked types of <input>
        CLICK_TYPES = {"radio", "checkbox", "submit", "image", "button"}
        self.__elem_dict: DefaultDict[OperationType, List[Element]] = defaultdict(list)
        for elem in self.__elems:
            bs_elem = elem.bs_elem
            for operation_type in [OperationType.CLICK, OperationType.ENTER, OperationType.SELECT]:
                if elem.name in Tags.get_target_tags(operation_type):
                    self.__elem_dict[operation_type].append(elem)
            if elem.name == "input":
                if "type" in bs_elem.attrs and bs_elem["type"] in CLICK_TYPES:
                    self.__elem_dict[OperationType.CLICK].append(elem)
                else:
                    self.__elem_dict[OperationType.ENTER].append(elem)

    def __extract_attr_words(self, bs_elem):
        words = []
        target_attrs = set(bs_elem.attrs) - Setting.EXCEPT_ATTRS
        for attr in target_attrs:
            if attr in bs_elem.attrs and bs_elem[attr] != "":
                if isinstance(bs_elem[attr], list):
                    joined_str = " ".join(bs_elem[attr])
                    words.extend(WordUtil.split(joined_str))
                else:
                    words.extend(WordUtil.split(bs_elem[attr]))
        words.extend(WordUtil.split(bs_elem.text))
        return WordUtil.filter(words)

    def __extract_text_words(self, bs_elem):
        words = []
        labels = self.__extract_label(bs_elem)
        for label in labels:
            words.extend(WordUtil.split(label))
        words.extend(WordUtil.split(bs_elem.text))
        return WordUtil.filter(words)

    def __extract_label(self, bs_elem):
        if "id" in bs_elem.attrs and bs_elem["id"] != "":
            elem_id = bs_elem["id"]
            labels = self.__page_manager.get_associated_labels(elem_id)
            return labels
        else:
            return []

    def __is_invisible(self, bs_elem):
        return (
            "type" in bs_elem.attrs
            and bs_elem["type"] == "hidden"
            or bs_elem.name == "a"
            and bs_elem.text == ""
        )
