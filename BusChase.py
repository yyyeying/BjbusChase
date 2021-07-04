import re
import numpy
from typing import Dict, List

from BusAppAutomator import BusAppAutomator
from Bus import Bus

MAX_DISTANCE = 1000


class BusChase(object):
    def __init__(self, lines: List[Dict[str, str]], start_station: str, end_station: str):
        self.bus_automator = BusAppAutomator()
        self.lines = lines
        self.start_station = start_station
        self.end_station = end_station
        self.bus_list = {}
        self.duration_list = {}
        for i in range(len(self.lines)):
            self.bus_list.update({self.lines[i]['route']: []})
            self.duration_list.update({self.lines[i]['route']: []})

    def chase(self):
        self.bus_automator.launch_driver()
        while True:
            for station in [self.start_station, self.end_station]:
                for route in self.lines:
                    self.process(route, station)

    def process(self, route, station):
        next_bus_info = self.bus_automator.query_line_info(route=route['route'],
                                                           direction=route['direction'],
                                                           station=station)
        if next_bus_info is not None:
            print('BusChase.process: next_bus_info {}'.format(next_bus_info))
            if station == self.start_station and next_bus_info['next_station'] == station:
                distance = re.split(r'(\d+)', next_bus_info['distance'])
                print('BusChase.process: distance {}'.format(distance))
                if distance[2] == '米' and int(distance[1]) <= MAX_DISTANCE:
                    bus_exist = False
                    for bus in self.bus_list[next_bus_info['route']]:
                        if bus.bus_id == next_bus_info['id']:
                            print('BusChase.process: update a bus start_time')
                            bus.start_time = next_bus_info['time']
                            bus_exist = True
                    if not bus_exist:
                        print('BusChase.process: add new bus')
                        new_bus = Bus(bus_number=next_bus_info['route'],
                                      bus_id=next_bus_info['id'],
                                      start_station=self.start_station,
                                      end_station=self.end_station)
                        new_bus.start_time = next_bus_info['time']
                        self.bus_list[next_bus_info['route']].append(new_bus)
            if station == self.end_station and next_bus_info['next_station'] == station:
                distance = re.split(r'(\d+)', next_bus_info['distance'])
                print('BusChase.process: distance {}'.format(distance))
                if distance[2] == '米' and int(distance[1]) <= MAX_DISTANCE:
                    bus_exist = False
                    for bus in self.bus_list[next_bus_info['route']]:
                        if bus.bus_id == next_bus_info['id']:
                            bus_exist = True
                            print('BusChase.process: update a bus end_time')
                            bus.end_time = next_bus_info['time']
                            self.duration_list[route['route']].append(int(bus.end_time) - int(bus.start_time))
                            bus.write_to_log()
                            self.bus_list[next_bus_info['route']].remove(bus)
                    if not bus_exist and len(self.duration_list[route['route']]) > 0:
                        # 补登
                        print('BusChase.process: add new bus')
                        new_bus = Bus(bus_number=next_bus_info['route'],
                                      bus_id=next_bus_info['id'],
                                      start_station=self.start_station,
                                      end_station=self.end_station)
                        new_bus.start_time = str(int(next_bus_info['time'])
                                                 - numpy.mean(self.duration_list[route['route']]))
                        new_bus.end_time = next_bus_info['time']
                        new_bus.write_to_log()
        else:
            print('BusChase.process: no next_bus_info')
        bus_not_finished = []
        for bus in self.bus_list[route['route']]:
            bus_not_finished.append(bus.bus_id)
        print('BusChase.process: route {} not finished bus {}'.format(route['route'], bus_not_finished))


if __name__ == '__main__':
    lines = [{'route': '1', 'direction': '四惠枢纽站-老山公交场站'},
             {'route': '52', 'direction': '平乐园-靛厂新村'}]
    bus_chase = BusChase(lines, '北京站口东', '复兴门内')
    bus_chase.chase()
