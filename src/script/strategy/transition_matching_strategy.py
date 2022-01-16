import itertools
import sys
import traceback
from collections import defaultdict
from math import e
from time import sleep
from typing import Dict, List, Optional, Tuple, Type, TypeVar

import Setting
from calculator import IdfCalculator, VectorCalculator
from page.driver_manager import DriverManager
from page.element import Element
from page.element_container import ElementContainer
from page.page_manager import PageManager
from script.operation import (CodableOperation, LocatableOperation,
                              PageTransition, Step)
from script.operation_type import OperationType
from script.script_writer import LocatorWriter
from script.strategy.strategy import Strategy
from script.test_case import TestCase
from util.word_util import WordUtil


class Variation:
    def __init__(
        self,
        variation: Tuple[Element, ...],
        score: float,
    ) -> None:
        self.__variation = variation
        self.__score = score

    def print(self, indent: int = 0):
        for enter in self.__variation:
            print("  " * indent, end="")
            print(enter.bs_elem)

    @property
    def score(self) -> float:
        return self.__score

    @property
    def variation(self) -> Tuple[Element, ...]:
        return self.__variation


class PageVariation:
    def __init__(self, variation: Dict[OperationType, Optional[Variation]]):
        self.__variation = variation

    def get(self, operation_type: OperationType) -> Optional[Variation]:
        return self.__variation[operation_type]

    @property
    def score(self) -> float:
        total = 0
        for operation_type in [OperationType.ENTER, OperationType.SELECT, OperationType.CLICK]:
            if self.get(operation_type) is not None:
                total += self.get(operation_type).score
        return total

    def to_code(self, codable_steps: List[CodableOperation]):
        indexes = defaultdict(int)
        test_script = []
        for step in codable_steps:
            if isinstance(step, LocatableOperation):
                if self.get(step.operation_type) is None:
                    continue
                nextStep = self.get(step.operation_type).variation[indexes[step.operation_type]]
                indexes[step.operation_type] += 1
                test_script.append(step.to_code(nextStep.get_locator()))
                LocatorWriter.append(nextStep.get_xpath())
            else:
                test_script.append(step.to_code())
        return test_script

    def print(self, indent: int = 0):
        for operation_type in [OperationType.ENTER, OperationType.SELECT, OperationType.CLICK]:
            if self.get(operation_type) is not None:
                self.get(operation_type).print(indent)
        print("  " * indent, end="")
        print(self.score)
        print("  " * indent, end="")
        print("------------")

    def easy_print(self):
        for operation_type in [OperationType.ENTER, OperationType.SELECT, OperationType.CLICK]:
            if self.get(operation_type) is not None:
                self.get(operation_type).print()


class SearchTree:
    def __init__(self, score: float, current: Optional[PageVariation]):
        self.__current = current
        self.__total_score = score
        self.__children = []

    @property
    def current(self) -> Optional[PageVariation]:
        return self.__current

    @property
    def children(self) -> List["SearchTree"]:
        return self.__children

    @property
    def total_score(self) -> float:
        return self.__total_score

    def print(self, depth: int = 0):
        if self.current is not None:
            print("  " * depth, end="")
            print("total: " + str(self.__total_score))
            self.current.print(depth)
        for node in self.children:
            node.print(depth + 1)


class State:
    def __init__(self, search_tree: SearchTree, path: List[PageVariation]):
        self.__search_tree = search_tree
        self.__page_variation = path

    @property
    def search_tree(self) -> SearchTree:
        return self.__search_tree

    @property
    def path(self) -> List[PageVariation]:
        return self.__page_variation


class TransitionMatchingStrategy(Strategy):
    def __init__(self, model):
        self.__driver_manager = DriverManager()
        self.__element_container = ElementContainer(PageManager(self.__driver_manager))
        self.__model = model
        self.__root = SearchTree(0, None)
        self.__best_path: List[PageVariation] = []

    def to_code(self, test_case: TestCase) -> str:
        try:
            locatable_operations_by_page = self.__filter_by_type_and_split(
                test_case.steps, LocatableOperation
            )

            self.__open = test_case.open
            self.__open.execute(self.__driver_manager)
            self.__beam_search([State(self.__root, [])], 0, locatable_operations_by_page)
            self.__root.print()
            test_script = []
            for codable_steps, page_variation in zip(
                self.__filter_by_type_and_split(test_case.steps, CodableOperation),
                self.__best_path,
            ):
                test_script += page_variation.to_code(codable_steps)
            return self.__construct_method_string(test_case.name, test_script)
        except Exception:
            print(e)
            traceback.print_exc()
            sys.exit(1)
        finally:
            self.__driver_manager.quit()

    def __construct_method_string(self, name, test_script) -> str:
        return """\
def {}(driver):
    {}
""".format(
            name, "\n    ".join(test_script)
        )

    def __beam_search(
        self,
        candidates: List[State],
        depth: int,
        page_steps: List[List[LocatableOperation]],
    ):
        if len(page_steps) <= depth:
            self.__best_path = candidates[0].path
            return
        next_candidates: List[State] = []
        for candidate in candidates:
            path = candidate.path
            tree = candidate.search_tree
            locatable_operations: List[LocatableOperation] = page_steps[depth]
            self.__execute_prev_transition(page_steps, path)
            page_variations = self.__get_page_variations(locatable_operations)
            for page_variation in page_variations[: Setting.SEARCH_WIDTH]:
                next_score = tree.total_score + page_variation.score
                next_page = SearchTree(next_score, page_variation)
                tree.children.append(next_page)
                next_candidates.append(State(next_page, path + [page_variation]))
        next_candidates.sort(key=lambda c: c.search_tree.total_score, reverse=True)
        self.__beam_search(next_candidates[: Setting.BEAM_WIDTH], depth + 1, page_steps)

    T = TypeVar("T", LocatableOperation, CodableOperation)

    def __filter_by_type_and_split(self, steps: List[Step], target_class: Type[T]) -> List[List[T]]:
        result = []
        page = []
        for step in steps:
            if isinstance(step, PageTransition):
                result.append(page)
                page = []
            elif isinstance(step, target_class):
                page.append(step)
        result.append(page)
        return result

    def __get_page_variations(self, steps_in_page: List[LocatableOperation]) -> List[PageVariation]:
        self.__element_container.extract_element()
        idf = IdfCalculator().calc(self.__element_container.elems)
        vector_calculator = VectorCalculator(self.__model, idf)
        self.__element_container.append_vector(vector_calculator)
        enter_variations = self.__get_variation_by_type(
            steps_in_page, vector_calculator, OperationType.ENTER
        )[: Setting.SEARCH_WIDTH]
        select_variations = self.__get_variation_by_type(
            steps_in_page, vector_calculator, OperationType.SELECT
        )[: Setting.SEARCH_WIDTH]
        click_variations = self.__get_variation_by_type(
            steps_in_page, vector_calculator, OperationType.CLICK
        )[: Setting.SEARCH_WIDTH]

        page_variations: List[PageVariation] = []
        for enter_variation, select_variation, click_variation in itertools.product(
            enter_variations, select_variations, click_variations
        ):
            page_variations.append(
                PageVariation(
                    {
                        OperationType.ENTER: enter_variation,
                        OperationType.SELECT: select_variation,
                        OperationType.CLICK: click_variation,
                    }
                )
            )

        return sorted(
            page_variations, key=lambda page_variation: page_variation.score, reverse=True
        )

    def __get_variation_by_type(
        self,
        steps_in_page: List[LocatableOperation],
        vector_calculator: VectorCalculator,
        operation_type: OperationType,
    ) -> List[Optional[Variation]]:
        steps = [step for step in steps_in_page if step.operation_type == operation_type]
        elems = self.__element_container.get_elems_of(operation_type)
        variations: List[Optional[Variation]] = []
        candidates_list = self.__filter_elements(elems, steps, vector_calculator)
        for elems_candidate in itertools.product(*candidates_list):
            if len(set(elems_candidate)) < len(elems_candidate):  # has duplicate
                continue
            score = 0
            for step, elem in zip(steps, elems_candidate):
                words = step.target.split()
                valid_words = WordUtil.filter(words)
                score += vector_calculator.get_similarity(valid_words, elem)
            if score != 0 and len(steps) > 0:
                score /= len(steps)
            variations.append(Variation(elems_candidate, score))
        if variations == []:
            return [None]
        else:
            return sorted(variations, key=lambda c: c.score, reverse=True)

    def __filter_elements(self, elems, steps: List[LocatableOperation], vector_calculator):
        candidates_list: List[List[Element]] = []
        for step in steps:
            candidates_with_similarity = []
            for elem in elems:
                words = step.target.split()
                valid_words = WordUtil.filter(words)
                similarity = vector_calculator.get_similarity(valid_words, elem)
                candidates_with_similarity.append([elem, similarity])
            candidates_with_similarity.sort(key=lambda x: x[1], reverse=True)
            min_num = min(Setting.PAGE_MATCHING_SEARCH, len(elems))
            candidates = list(
                map(lambda candidate: candidate[0], candidates_with_similarity[:min_num])
            )
            candidates_list.append(candidates)
        return candidates_list

    def __execute_page_variation(
        self,
        steps_in_page: List[LocatableOperation],
        page_variation: PageVariation,
    ):
        indexes = defaultdict(int)
        for step in steps_in_page:
            if isinstance(step, LocatableOperation):
                if page_variation.get(step.operation_type) is None:
                    continue
                nextStep = page_variation.get(step.operation_type).variation[
                    indexes[step.operation_type]
                ]
                indexes[step.operation_type] += 1
                try:
                    step.execute(nextStep.get_locator(), self.__driver_manager)
                except Exception:
                    pass

    def __execute_prev_transition(
        self, page_steps: List[List[LocatableOperation]], path: List[PageVariation]
    ):
        if path == []:
            return
        if Setting.RESTART_DRIVER:
            self.__driver_manager.quit()
            self.__driver_manager = DriverManager()
            self.__element_container = ElementContainer(PageManager(self.__driver_manager))
        self.__open.execute(self.__driver_manager)
        for steps, variation in zip(page_steps, path):
            self.__execute_page_variation(steps, variation)
            sleep(Setting.TRANSITION_SLEEP_TIME)
