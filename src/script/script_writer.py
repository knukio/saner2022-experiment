import datetime

import Setting

from script.locator import Locator


class ScriptWriter:
    def write(self, method_string: str, generation_time: float, model_load_time: float):
        date = datetime.datetime.now().strftime("%y%m%d%H%M")
        suffix = "{}_{}_{}_{}_{}_{}".format(
            date,
            Setting.TESTCASE_FILE,
            Setting.MODEL.name,
            Setting.SEARCH_WIDTH,
            Setting.BEAM_WIDTH,
            Setting.TEXT_WEIGHT,
        )
        filename = "{}/test_script_{}.py".format(Setting.OUTPUT_DIRECTORY, suffix)
        script = f"""\
# date : {date}
# model: {Setting.MODEL.name}
# search width: {Setting.SEARCH_WIDTH}
# beam width: {Setting.BEAM_WIDTH}
# text weight: {Setting.TEXT_WEIGHT}
# model load time: {model_load_time}
# generation time: {generation_time}
from selenium.webdriver.support.select import Select
{method_string}
"""
        with open(filename, mode="w") as f:
            f.write(script)


class LocatorWriter:
    __script = ""

    @classmethod
    def append(cls, locator: Locator):
        cls.__script += locator.value + ", "

    @classmethod
    def end_testcase(cls):
        cls.__script = cls.__script[:-2]
        cls.__script += "\n"

    @classmethod
    def write(cls):
        date = datetime.datetime.now().strftime("%y%m%d%H%M")
        suffix = "{}_{}_{}_{}_{}_{}".format(
            date,
            Setting.TESTCASE_FILE,
            Setting.MODEL.name,
            Setting.SEARCH_WIDTH,
            Setting.BEAM_WIDTH,
            Setting.TEXT_WEIGHT,
        )
        filename = "{}/locator_{}.csv".format(Setting.OUTPUT_DIRECTORY, suffix)
        with open(filename, mode="w") as f:
            f.write(cls.__script)
