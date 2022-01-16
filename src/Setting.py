from model import ModelType

# Basic
BINARY_LOCATION = "/usr/bin/google-chrome"
CHROMEDRIVER_LOCATION = "/usr/local/bin/chromedriver"
MODEL_LOCATION = "data"
TESTCASE_DIR = "experiment"
TESTCASE_FILE = "mantisbt_all"
ALL_TESTCASE = False # Run all test case
TESTCASES = ["create_custom_fields"] # test case set to run if ALL_TESTCASE==false
OUTPUT_DIRECTORY = "test_script"
WRITE_LOCATOR = False

# Common
MODEL = ModelType.FASTTEXT_300 
HEADLESS = False  # Chrome headless
SLEEP_TIME = 0  # wait between operations
TRANSITION_SLEEP_TIME = 0  # wait after page transition
SHOW_OPERATION = False
IDF_WEIGHT = 1.5  # The closer to 1, the bigger
TAG_CLICK = {"button", "img", "a"}  # click target tags

# Transition-level search
RESTART_DRIVER = True
SEARCH_WIDTH = 5
BEAM_WIDTH = 5
PAGE_MATCHING_SEARCH = 10  # explore top n
TEXT_WEIGHT = 3  # against attr_words

EXCEPT_ATTRS = {
    "class",
    "autocorrect",
    "spellcheck",
    "tabindex",
    "style",
    "pattern",
    "aria-hidden",
    "maxlength",
    "minlength",
    "max",
    "min",
    "height",
    "width",
    "size",
    "step",
}

STOP_WORDS = {
    "for",
    "the",
    "do",
    "did",
    "does",
    "this",
    "to",
    "of",
    "with",
    "and",
    "or",
    "have",
    "has",
    "as",
    "is",
}

HEURISTIC_STOP_WORDS = {
    "button",
    "btn",
    "link",
    "form",
    "svg",
    "www",
    "https",
    "http",
    "com",
    "js",
    "css",
    "true",
    "false",
    "checked",
}
