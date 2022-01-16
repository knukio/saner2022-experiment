from re import finditer, split
from typing import List

import Setting


class WordUtil:
    @classmethod
    def filter(cls, words: List[str]):
        return [
            word
            for word in cls.__to_lower(words)
            if len(word) >= 2 and word not in Setting.STOP_WORDS | Setting.HEURISTIC_STOP_WORDS
        ]

    @classmethod
    def split(cls, s):
        words = []
        for w in [word for word in split("[!-/:-@¥[-`{-~\\s]", s) if word != ""]:
            words.extend(cls.__camel_case_split(w))
        return words

    @classmethod
    def __to_lower(cls, words):
        return [str.lower(word) for word in words]

    @classmethod
    def __camel_case_split(cls, identifier):
        matches = finditer(".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier)
        return [m.group(0) for m in matches]
