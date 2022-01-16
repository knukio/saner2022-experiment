from collections import defaultdict
from math import log
from typing import List

from numpy import average, dot
from numpy.linalg import norm

import Setting
from model import Model, ModelType
from page.element import Element


class IdfCalculator:
    def calc(self, elems: List[Element]):
        idf = {}
        word_cnt = defaultdict(int)
        for elem in elems:
            occur = set()
            for word in elem.attr_words + elem.text_words:
                if word not in occur:
                    word_cnt[word] += 1
                    occur.add(word)
        elem_cnt = len(elems)
        for word in word_cnt.keys():
            idf[word] = log(elem_cnt / word_cnt[word], Setting.IDF_WEIGHT)

        return idf


class VectorCalculator:
    def __init__(self, model: Model, idf):
        self.__model = model
        self.__idf = idf

    def get_elem_vector(self, elem: Element):
        return self.__get_words_vector_weighted(elem.attr_words)

    def get_text_vector(self, elem: Element):
        if len(elem.text_words) != 0:
            return self.__get_words_vector_weighted(elem.text_words)
        else:
            return None

    def get_similarity(self, query, elem: Element) -> float:
        query_vector = self.__get_words_vector(query)
        cos_sim_words = self.__cosine_similarity(query_vector, elem.attr_vector)
        if len(elem.text_words) != 0:
            cos_sim_text = self.__cosine_similarity(query_vector, elem.text_vector)
            return (cos_sim_words + Setting.TEXT_WEIGHT * cos_sim_text) / (1 + Setting.TEXT_WEIGHT)
        else:
            return cos_sim_words

    def __get_words_vector_weighted(self, words):
        vector = []
        weights = []
        for word in words:
            if (
                Setting.MODEL not in [ModelType.FASTTEXT_300, ModelType.FASTTEXT_300_SMALL]
                and word not in self.__model.vocab
            ):
                vector.append([0.5] * self.__model.get_dimension())
            else:
                vector.append(self.__model.get_vector(word))
            weights.append(self.__idf[word])

        return average(vector, axis=0, weights=weights)

    def __get_words_vector(self, words):
        vector = []
        for word in words:
            if (
                Setting.MODEL not in [ModelType.FASTTEXT_300, ModelType.FASTTEXT_300_SMALL]
                and word not in self.__model.vocab
            ):
                vector.append([0.5] * self.__model.get_dimension())
            else:
                vector.append(self.__model.get_vector(word))
        return average(vector, axis=0)

    def __cosine_similarity(self, a, b):
        return dot(a, b) / (norm(a) * norm(b))
