import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import StaleElementReferenceException

from AppAutomator import AppAutomator

BTN_PERMISSION_ALLOW = 'com.lbe.security.miui:id/permission_allow_foreground_only_button'
BTN_DO_NOT_UPDATE = 'android:id/button2'
BTN_CONFIRM = 'android:id/button1'
BTN_AGREE = 'com.aibang.bjtraffic:id/confirm'
BTN_BACK = 'com.aibang.bjtraffic:id/btn_back'
BTN_BUS_CORRECT = 'com.aibang.bjtraffic:id/bus_corrent'
BTN_RIGHT = 'com.aibang.bjtraffic:id/btn_right'
BTN_SEARCH = 'com.aibang.bjtraffic:id/search'
TEXT_EDIT_LINE = 'com.aibang.bjtraffic:id/line_edit'
TEXT_EDIT_STATION = 'com.aibang.bjtraffic:id/station_edit'
VIEW_LINE_NAME = 'com.aibang.bjtraffic:id/line_name'
VIEW_BUS_ID = 'com.aibang.bjtraffic:id/busIdTv'
VIEW_NEXT_STATION = 'com.aibang.bjtraffic:id/nextStationTv'
VIEW_DISTANCE = 'com.aibang.bjtraffic:id/distanceToNextStationTv'
VIEW_STATION_NAME = 'com.aibang.bjtraffic:id/station_name'
CLASS_TEXTVIEW = 'android.widget.TextView'

PACKAGE_NAME = 'com.aibang.bjtraffic'

ACTIVITY_LAUNCHER = '.launcher.Launcher'
ACTIVITY_PERMISSION = 'com.android.packageinstaller.permission.ui.GrantPermissionsActivity'
ACTIVITY_BOOT = '.boot.BootActivity'
ACTIVITY_MAIN = '.main.MainActivity'
ACTIVITY_NEXTBUS_MAIN = '.nextbus.main.NextBusMainActivity'
ACTIVITY_NEXTBUS_DETAIL = 'com.aibang.nextbus.NextBusDetailActivity'
ACTIVITY_NEXTBUS_MAP = 'com.aibang.nextbus.NextBusMapActivity'
ACTIVITY_NEXTBUS_CORRECT = 'com.aibang.nextbus.correct.BusCorrectActivity'

MAX_RETRY = 5


class BusAppAutomator(AppAutomator):
    def __init__(self):
        AppAutomator.__init__(self,
                              package=PACKAGE_NAME,
                              activity=ACTIVITY_BOOT)
        self.activity_list = {ACTIVITY_LAUNCHER: -1,
                              ACTIVITY_PERMISSION: 0,
                              ACTIVITY_BOOT: 1,
                              ACTIVITY_MAIN: 2,
                              ACTIVITY_NEXTBUS_MAIN: 3,
                              ACTIVITY_NEXTBUS_DETAIL: 4,
                              ACTIVITY_NEXTBUS_MAP: 5,
                              ACTIVITY_NEXTBUS_CORRECT: 6}
        self.functions = {ACTIVITY_PERMISSION: self.activity_permission_operation,
                          ACTIVITY_BOOT: self.activity_boot_operation,
                          ACTIVITY_MAIN: self.activity_main_operation,
                          ACTIVITY_LAUNCHER: self.activity_launcher_operation,
                          ACTIVITY_NEXTBUS_MAIN: self.activity_nextbus_main_operation,
                          ACTIVITY_NEXTBUS_DETAIL: self.activity_nextbus_detail_operation,
                          ACTIVITY_NEXTBUS_MAP: self.activity_nextbus_map_operation,
                          ACTIVITY_NEXTBUS_CORRECT: self.activity_nextbus_correct_operation}
        self.route = None
        self.direction = None
        self.station = None
        self.retry = 0

    def launch_driver(self):
        self.init_connection()
        self.driver = self.init_appium_driver()
        # self.driver.implicitly_wait(1)

    def reach_activity(self, activity: str):
        '''
        前往目标Activity
        :param activity: 目标Activity
        :return:
        '''
        print('BusAppAutomator.reach_activity: destination {}'.format(activity))
        while self.driver.current_activity != activity and self.retry < MAX_RETRY:
            print('BusAppAutomator.reach_activity: current activity {}'.format(self.driver.current_activity))
            try:
                forward = int(self.activity_list[self.driver.current_activity] - self.activity_list[activity])
                self.functions[self.driver.current_activity](forward)
            except KeyError:
                self.activity_launcher_operation(forward)

    def activity_launcher_operation(self, forward: int):
        print('BusAppAutomator.activity_launcher_operation: APP not started, restart driver.')
        self.driver = self.init_appium_driver()

    def activity_permission_operation(self, forward: int):
        if forward < 0:
            self.click_element(BTN_PERMISSION_ALLOW)
            return
        else:
            return

    def activity_boot_operation(self, forward: int):
        if forward < 0:
            return
        else:
            return

    def activity_main_operation(self, forward: int):
        if forward < 0:
            self.click_element(BTN_DO_NOT_UPDATE)
            self.click_element(BTN_AGREE)
            try:
                self.driver.find_element_by_xpath("//*[@text='实时公交']").click()
            except NoSuchElementException:
                pass
            return

    def activity_nextbus_main_operation(self, forward: int):
        if forward < 0:
            # 输入线路
            # print(self.driver.current_activity)
            route_info = '{}({})'.format(self.route, self.direction)
            try:
                self.driver.find_element_by_id(TEXT_EDIT_LINE).send_keys(route_info)
            except NoSuchElementException:
                print('BusAppAutomator.activity_nextbus_main_operation: NoSuchElementException {}'
                      .format(TEXT_EDIT_LINE))
                pass
            except StaleElementReferenceException:
                print('BusAppAutomator.activity_nextbus_main_operation: StaleElementReferenceException {}'
                      .format(TEXT_EDIT_LINE))
                pass
            self.click_element(VIEW_LINE_NAME)
            print('BusAppAutomator.activity_nextbus_main_operation: Select route: {}'
                  .format(route_info))
            # 选择车站
            self.click_element(TEXT_EDIT_STATION)
            try:
                self.driver.swipe(540, 800, 540, 1200, duration=100)    # 滑到最上方
            except InvalidElementStateException:
                pass
            find_station = False
            retry = 0
            while not find_station and retry < MAX_RETRY:
                try:
                    station_list = self.driver.find_elements_by_id(VIEW_STATION_NAME)
                    for s in station_list:
                        if s.text == self.station:
                            print('BusAppAutomator.activity_nextbus_main_operation: Select station: {}'.format(s.text))
                            s.click()
                            find_station = True
                            self.click_element(BTN_SEARCH)
                            return
                except StaleElementReferenceException:
                    print('BusAppAutomator.activity_nextbus_main_operation: StaleElementReferenceException')
                    retry += 1
                    return
                try:
                    self.driver.swipe(540, 1000, 540, 800, duration=200)
                except InvalidElementStateException:
                    print('BusAppAutomator.activity_nextbus_main_operation: InvalidElementStateException')
                    retry += 1
                    return
                retry += 1
            return
        else:
            return

    def activity_nextbus_detail_operation(self, forward: int):
        if forward < 0:
            # 进入地图
            self.click_element(BTN_RIGHT)
            return
        elif forward > 0:
            # 返回
            self.click_element(BTN_BACK)
            return
        else:
            return

    def activity_nextbus_map_operation(self, forward: int):
        if forward < 0 and self.retry < MAX_RETRY:
            print('BusAppAutomator.activity_nextbus_map_operation: in NextBusMapActivity forward {}'.format(self.retry))
            # 进入纠错
            bus_correct_btn = None
            retry = 0
            while bus_correct_btn is None and retry < MAX_RETRY:
                # self.driver.tap([(920, 120)], 50)  # 右上角菜单点按无效
                self.click_element(BTN_RIGHT)
                try:
                    bus_correct_btn = self.driver.find_element_by_id(BTN_BUS_CORRECT)
                except NoSuchElementException:
                    print('BusAppAutomator.activity_nextbus_map_operation: NoSuchElementException')
                    retry += 1
                    continue
                retry += 1
            if bus_correct_btn is not None:
                try:
                    bus_correct_btn.click()
                except StaleElementReferenceException:
                    print('BusAppAutomator.activity_nextbus_map_operation: StaleElementReferenceException')
                    pass
                try:
                    time.sleep(0.5)
                    self.driver.tap([(540, 980)])
                except InvalidElementStateException:
                    pass
            self.retry += 1
            return
        elif forward > 0:
            # 返回
            self.click_element(BTN_BACK)
            return
        else:
            print('BusAppAutomator.activity_nextbus_map_operation: reach MAX_RETRY')
            return

    def activity_nextbus_correct_operation(self, forward: int):
        if forward < 0:
            return
        elif forward > 0:
            self.click_element(BTN_BACK)
            self.click_element(BTN_CONFIRM)
            return

    def query_line_info(self,
                        route='1',
                        direction='老山公交场站-四惠枢纽站',
                        station='八王坟西'):
        self.route = route
        self.direction = direction
        self.station = station
        self.retry = 0
        self.reach_activity(ACTIVITY_NEXTBUS_MAIN)
        self.reach_activity(ACTIVITY_NEXTBUS_CORRECT)
        if self.retry < MAX_RETRY:
            print('BusAppAutomator.query_line_info: get next_bus_info')
            try:
                next_bus_info = {'route': route,
                                 'id': self.driver.find_element_by_id(VIEW_BUS_ID).text,
                                 'next_station': self.driver.find_element_by_id(VIEW_NEXT_STATION).text,
                                 'distance': self.driver.find_element_by_id(VIEW_DISTANCE).text,
                                 'time': time.time()}
                return next_bus_info
            except NoSuchElementException:
                print('BusAppAutomator.query_line_info: NoSuchElementException')
                return None
            except InvalidElementStateException:
                print('BusAppAutomator.query_line_info: InvalidElementStateException')
                return None
            except StaleElementReferenceException:
                print('BusAppAutomator.query_line_info: StaleElementReferenceException')
        else:
            print('BusAppAutomator.query_line_info: Reach MAX_RETRY')
            return None


if __name__ == '__main__':
    bus_automator = BusAppAutomator()
    bus_automator.launch_driver()
    for i in range(10):
        next_bus_info = bus_automator.query_line_info(route='夜4',
                                                      direction='安宁庄东路南口-菜户营桥东',
                                                      station='西单商场')
        print(next_bus_info)
