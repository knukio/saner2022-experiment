from abc import ABCMeta, abstractmethod
from typing import List

from script.test_case import TestCase


class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def to_code(self, test_case: TestCase) -> List[str]:
        pass
