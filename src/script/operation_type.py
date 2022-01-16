from enum import Enum


class OperationType(Enum):
    ENTER = "enter"
    SELECT = "select"
    CLICK = "click"
    OPEN = "open"
    PAGE_TRANSITION = "page_transition"
    ASSERT_ELEMENT = "assert element"
    ASSERT_STRING = "assert string"
    ASSERT_TITLE = "assert title"
