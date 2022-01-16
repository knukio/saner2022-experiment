from abc import ABCMeta, abstractmethod, abstractproperty
from time import sleep
from typing import Optional

import Setting
from page.driver_manager import DriverManager

from script.locator import Locator, LocatorType
from script.operation_type import OperationType


class Step(metaclass=ABCMeta):
    def __init__(self, raw_string: str):
        self.__raw_string = raw_string

    @property
    def raw_string(self):
        return self.__raw_string

    @abstractproperty
    def operation_type(self) -> OperationType:
        return OperationType.PAGE_TRANSITION


class CodableOperation(Step, metaclass=ABCMeta):
    @abstractmethod
    def to_code(self) -> str:
        pass


class ExecutableOperation(CodableOperation, metaclass=ABCMeta):
    def __init__(self, raw_string: str):
        super().__init__(raw_string)

    @abstractmethod
    def execute(self, driver_manager: DriverManager) -> str:
        pass


class LocatableOperation(ExecutableOperation, metaclass=ABCMeta):
    def __init__(self, raw_string: str, target: str, once: bool):
        super().__init__(raw_string)
        self.__target = target
        self.__once = once

    @property
    def target(self) -> str:
        return self.__target

    @property
    def once(self) -> bool:
        return self.__once

    @abstractmethod
    def to_code(self, locator: Locator) -> str:
        pass

    @abstractmethod
    def execute(self, locator: Locator, driver_manager: DriverManager) -> str:
        pass

    def get_locator(self) -> Optional[Locator]:
        if self.target[0] == "#":
            return Locator(LocatorType.ID, self.target[1:])
        elif self.target[0:6] == "xpath:":
            return Locator(LocatorType.XPATH, self.target[6:])
        elif self.target[0:5] == "link:":
            return Locator(LocatorType.LINK_TEXT, self.target[5:])
        else:
            return None


class Open(ExecutableOperation):
    def __init__(self, raw_string: str, value: str):
        Step.__init__(self, raw_string)
        self.__value = value

    @property
    def value(self) -> str:
        return self.__value

    @property
    def operation_type(self) -> OperationType:
        return OperationType.OPEN

    def to_code(self):
        return "driver.get('{}')".format(self.value)

    def execute(self, driver_manager: DriverManager) -> None:
        driver_manager.open(self.value)
        sleep(Setting.TRANSITION_SLEEP_TIME)


class Enter(LocatableOperation):
    def __init__(self, raw_string: str, target: str, value: str, once: bool):
        LocatableOperation.__init__(self, raw_string, target, once)
        self.__value = value

    @property
    def value(self) -> str:
        return self.__value

    @property
    def operation_type(self) -> OperationType:
        return OperationType.ENTER

    def to_code(self, locator: Locator):
        return (
            "driver.find_element_by_{}('{}').clear()".format(
                locator.locator_type.value, locator.value
            )
            + "\n    "
            + "driver.find_element_by_{}('{}').send_keys('{}')".format(
                locator.locator_type.value, locator.value, self.value
            )
        )

    def execute(self, locator: Locator, driver_manager: DriverManager) -> None:
        sleep(Setting.SLEEP_TIME)
        if Setting.SHOW_OPERATION:
            print("enter {} in {}".format(self.value, locator.value))
        driver_manager.enter(locator, self.value)


class Select(LocatableOperation):
    def __init__(self, raw_string: str, target: str, value: str, once: bool):
        LocatableOperation.__init__(self, raw_string, target, once)
        self.__value = value

    @property
    def value(self) -> str:
        return self.__value

    @property
    def operation_type(self) -> OperationType:
        return OperationType.SELECT

    def to_code(self, locator: Locator):
        return "Select(driver.find_element_by_{}('{}')).select_by_visible_text('{}')".format(
            locator.locator_type.value, locator.value, self.value
        )

    def execute(self, locator: Locator, driver_manager: DriverManager) -> None:
        sleep(Setting.SLEEP_TIME)
        if Setting.SHOW_OPERATION:
            print("select {} from {}".format(self.value, locator.value))
        driver_manager.select(locator, self.value)


class Click(LocatableOperation):
    def __init__(self, raw_string: str, target: str, once: bool):
        LocatableOperation.__init__(self, raw_string, target, once)

    @property
    def operation_type(self) -> OperationType:
        return OperationType.CLICK

    def to_code(self, locator: Locator):
        return "driver.find_element_by_{}('{}').click()".format(
            locator.locator_type.value, locator.value
        )

    def execute(self, locator: Locator, driver_manager: DriverManager) -> None:
        sleep(Setting.SLEEP_TIME)
        if Setting.SHOW_OPERATION:
            print("click {}".format(locator.value))
        driver_manager.click(locator)


class AssertTitle(CodableOperation):
    def __init__(self, raw_string: str, value: str):
        Step.__init__(self, raw_string)
        self.__value = value

    @property
    def value(self) -> str:
        return self.__value

    @property
    def operation_type(self) -> OperationType:
        return OperationType.ASSERT_TITLE

    def to_code(self) -> str:
        return "assert '{}' == driver.title, 'expected title: \"{}\", but actual: \"{{}}\"'.format(driver.title)".format(
            self.value, self.value
        )


class AssertString(CodableOperation):
    def __init__(self, raw_string: str, value: str):
        Step.__init__(self, raw_string)
        self.__value = value

    @property
    def value(self) -> str:
        return self.__value

    @property
    def operation_type(self) -> OperationType:
        return OperationType.ASSERT_STRING

    def to_code(self) -> str:
        return "assert '{}' in driver.page_source, 'string \"{}\" is not exist'".format(
            self.value, self.value
        )


class PageTransition(Step):
    def __init__(self, raw_string):
        Step.__init__(self, raw_string)

    @property
    def operation_type(self) -> OperationType:
        return OperationType.PAGE_TRANSITION
