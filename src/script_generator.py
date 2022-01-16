import traceback
from time import time

import Setting
from model import Model
from script.script_writer import LocatorWriter, ScriptWriter
from script.strategy.strategy import Strategy
from script.strategy.transition_matching_strategy import \
    TransitionMatchingStrategy
from script.test_case import TestCaseParser

start = time()
parser = TestCaseParser()
try:
    test_cases = parser.load_file(Setting.TESTCASE_DIR + "/" + Setting.TESTCASE_FILE + ".yaml")
    print("loading model...")
    model = Model(Setting.MODEL)
    model_load_time = time() - start
    print("start generation")
    script = ""
    for test_case in test_cases:
        print("--------------------")
        print(test_case.name)
        print("--------------------")
        strategy: Strategy = TransitionMatchingStrategy(model)
        method_string = strategy.to_code(test_case)
        LocatorWriter.end_testcase()
        script += "\n"
        script += method_string
    writer = ScriptWriter()
    generation_time = time() - start - model_load_time
    writer.write(script, generation_time, model_load_time)
    if Setting.WRITE_LOCATOR:
        LocatorWriter.write()

except Exception as e:
    print(e)
    traceback.print_exc()
finally:
    elapsed_time = time() - start
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
