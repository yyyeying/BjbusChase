import os
import time
import csv


class Bus(object):
    def __init__(self, bus_number: str, bus_id: str, start_station: str, end_station: str):
        self.bus_number = bus_number
        self.bus_id = bus_id
        self.start_station = start_station
        self.start_time = 0
        self.end_station = end_station
        self.end_time = 0
        self.log_path = os.path.join(os.getcwd(),
                                     '{}_{}.csv'.format(self.bus_number,
                                                        time.strftime("%Y%m%d", time.localtime())))

    def is_finished(self) -> bool:
        return self.start_time < self.end_time

    def duration(self) -> str:
        duration = int(float(self.end_time)) - int(float(self.start_time))
        return '{}:{}'.format(str(int(duration / 60)), str(duration % 60))

    def write_to_log(self):
        log_content = [self.bus_id,
                       self.start_station,
                       self.end_station,
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(float(self.start_time)))),
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(float(self.end_time)))),
                       self.duration()]
        with open(self.log_path, 'a', newline="", encoding='utf-8-sig') as logfile:
            writer = csv.writer(logfile)
            writer.writerow(log_content)
            print('Bus.write_to_log')


if __name__ == '__main__':
    for i in range(10):
        bus = Bus('1', '30682', '八王坟东', '天安门东')
        time_a = str(time.time())
        bus.start_time = time_a
        bus.end_time = time.time()
        bus.write_to_log()
