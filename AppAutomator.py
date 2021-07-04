import os
from appium import webdriver
import selenium.common.exceptions as selenium_exceptions

MAX_RETRY = 5


class AppAutomator(object):
    def __init__(self, package="", activity=""):
        self.caps = {"platformName": "Android",
                     "platformVersion": "",
                     "deviceName": "",
                     "appPackage": package,
                     "appActivity": activity}
        self.server = 'http://localhost:4723/wd/hub'
        self.driver = None

    def init_connection(self):
        status = self.adb_connect()
        if status:
            print('AppAutomator.init_connection: Device connected.')
        self.caps['deviceName'] = self.adb_get_device_name()
        self.caps['platformVersion'] = self.adb_get_system_version()

    def adb_connect(self) -> bool:
        device_list = os.popen('adb devices').read()
        device_list = device_list.split('\n')
        if len(device_list) > 3:
            os.popen('adb -d')
            return True
        else:
            return False

    def adb_get_device_name(self) -> str:
        device_name = os.popen('adb devices').read()
        device_name = device_name.split('\n')[1]
        device_name = device_name.split('\t')[0]
        print('AppAutomator.adb_get_device_name: Device Name {}'.format(device_name))
        return device_name

    def adb_get_system_version(self) -> str:
        system_version = os.popen('adb shell getprop ro.build.version.release').read()
        system_version = system_version + '.0.0'
        return system_version

    def init_appium_driver(self) -> webdriver.Remote:
        driver = webdriver.Remote(self.server, self.caps)
        return driver

    def click_element(self, id) -> bool:
        button = None
        retry = 0
        while button is None and retry < MAX_RETRY:
            try:
                button = self.driver.find_element_by_id(id)
                button.click()
                return True
            except selenium_exceptions.NoSuchElementException:
                print('AppAutomator.click_element: NoSuchElementException {}'.format(id))
                retry += 1
                continue
            except selenium_exceptions.StaleElementReferenceException:
                print('AppAutomator.click_element: StaleElementReferenceException {}'.format(id))
                retry += 1
                continue


if __name__ == '__main__':
    automator = AppAutomator()
    automator.init_connection()
