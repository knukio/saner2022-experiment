import Setting
from script.locator import Locator, LocatorType
from selenium import webdriver
from selenium.common.exceptions import (NoAlertPresentException,
                                        UnexpectedAlertPresentException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select


class DriverManager:
    def __init__(self):
        options = Options()
        options.binary_location = Setting.BINARY_LOCATION
        options.add_experimental_option("prefs", {"intl.accept_languages": "en_US"})
        options.add_argument("--no-sandbox")
        if Setting.HEADLESS:
            options.add_argument("--headless")
        self.__driver = webdriver.Chrome(Setting.CHROMEDRIVER_LOCATION, chrome_options=options)

    def quit(self):
        self.__driver.quit()

    def open(self, url):
        try:
            self.__driver.get(url)
        except UnexpectedAlertPresentException:
            try:
                alert = self.__driver.switch_to_alert()
                alert.accept()
                print("Alert accepted")
                self.__driver.get(url)
            except NoAlertPresentException:
                pass

    def enter(self, locator: Locator, value: str):
        element = self.__locate(locator)
        element.clear()
        element.send_keys(value)

    def select(self, locator: Locator, value: str):
        element = self.__locate(locator)
        Select(element).select_by_visible_text(value)

    def click(self, locator: Locator):
        element = self.__locate(locator)
        element.click()

    def get_page_source(self) -> str:
        try:
            return self.__driver.page_source
        except UnexpectedAlertPresentException:
            try:
                alert = self.__driver.switch_to_alert()
                alert.accept()
                print("Alert accepted")
                return self.__driver.page_source
            except NoAlertPresentException:
                return ""

    def __locate(self, locator: Locator):
        if locator.locator_type == LocatorType.NAME:
            return self.__driver.find_element_by_name(locator.value)
        elif locator.locator_type == LocatorType.ID:
            return self.__driver.find_element_by_id(locator.value)
        elif locator.locator_type == LocatorType.LINK_TEXT:
            return self.__driver.find_element_by_link_text(locator.value)
        elif locator.locator_type == LocatorType.XPATH:
            return self.__driver.find_element_by_xpath(locator.value)
