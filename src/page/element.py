from script.locator import Locator, LocatorType


class Element:
    def __init__(self, bs_elem, id_, attr_words, text_words):
        self.__bs_elem = bs_elem
        self.__id = id_
        self.__name = bs_elem.name
        self.__xpath = self.__get_xpath()
        self.__attr_words = attr_words
        self.__text_words = text_words
        self.__attr_vector = []
        self.__text_vector = []

    @property
    def id(self):
        return self.__id

    @property
    def bs_elem(self):
        return self.__bs_elem

    @property
    def name(self):
        return self.__name

    @property
    def attr_words(self):
        return self.__attr_words

    @property
    def text_words(self):
        return self.__text_words

    @property
    def attr_vector(self):
        return self.__attr_vector

    @attr_vector.setter
    def attr_vector(self, vector):
        self.__attr_vector = vector

    @property
    def text_vector(self):
        return self.__text_vector

    @text_vector.setter
    def text_vector(self, text_vector):
        self.__text_vector = text_vector

    @property
    def xpath(self):
        return self.__xpath

    def get_locator(self):
        attrs = self.bs_elem.attrs
        if "id" in attrs:
            return Locator(LocatorType.ID, attrs["id"])
        elif "name" in attrs:
            if "type" in attrs and attrs["type"] == "radio":
                return Locator(LocatorType.XPATH, self.__get_xpath())
            else:
                return Locator(LocatorType.NAME, attrs["name"])
        else:
            return Locator(LocatorType.XPATH, self.__get_xpath())

    def get_xpath(self):
        return Locator(LocatorType.XPATH, self.__get_xpath())

    def __get_xpath(self):
        components = []
        child = self.bs_elem if self.bs_elem.name else self.bs_elem.parent
        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name
                if 1 == len(siblings)
                else "%s[%d]"
                % (child.name, next(i for i, s in enumerate(siblings, 1) if s is child))
            )
            child = parent
        components.reverse()
        return "/%s" % "/".join(components)
