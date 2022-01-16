import re
import shlex
import sys
from typing import List

import Setting
import yaml

from script.operation import (
    AssertString,
    AssertTitle,
    Click,
    Enter,
    Open,
    PageTransition,
    Select,
    Step,
)


class TestCase:
    def __init__(self, name, steps):
        if isinstance(steps[0], Open):
            self.__open: Open = steps[0]
        else:
            print("テストケースの最初の命令はopenである必要があります")
            sys.exit(1)
        self.__steps: List[Step] = steps
        self.__name = name

    @property
    def open(self) -> Open:
        return self.__open

    @property
    def steps(self) -> List[Step]:
        return self.__steps

    @property
    def name(self) -> str:
        return self.__name


class TestCaseParser:
    def load_file(self, filepath: str) -> List[TestCase]:
        test_cases = []
        with open(filepath) as file:
            test_suite = yaml.safe_load(file)
            for name, raw_steps in test_suite.items():
                if not Setting.ALL_TESTCASE and name not in Setting.TESTCASES:
                    continue
                steps = []
                for raw_step in raw_steps:
                    tokens = shlex.split(raw_step)
                    if re.fullmatch(r'open "[^"]+"', raw_step):
                        step = Open(raw_step, tokens[1])
                    elif re.fullmatch(r'enter "[^"]+" in "[^"]+"', raw_step):
                        step = Enter(raw_step, tokens[3], tokens[1], False)
                    elif re.fullmatch(r'select "[^"]+" from "[^"]+"', raw_step):
                        step = Select(raw_step, tokens[3], tokens[1], False)
                    elif re.fullmatch(r'click "[^"]+"', raw_step):
                        step = Click(raw_step, tokens[1], False)
                    elif re.fullmatch(r'assert string "[^"]+" exist', raw_step):
                        step = AssertString(raw_step, tokens[2])
                    elif re.fullmatch(r'assert title is "[^"]+"', raw_step):
                        step = AssertTitle(raw_step, tokens[3])
                    elif re.fullmatch(r"---", raw_step):
                        step = PageTransition(raw_step)
                    else:
                        raise ValueError("test case is invalid: {}".format(raw_step))
                    steps.append(step)
                test_cases.append(TestCase(name, steps))
        return test_cases
