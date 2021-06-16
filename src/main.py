import os
import datetime as dt
import argparse

from flask import Flask, render_template, request

app = Flask(__name__)

DATA_PATH = '../data'
ABBR_FILE = 'abbreviations.txt'
START_LOG_FILE = 'start.log'
END_LOG_FILE = 'end.log'


class Driver:
    """
    A class to represent a driver.

    Attributes
    ----------
    abbr : str
        name abbreviation as in abbreviation file
    name : str
        driver's name
    team : str
        driver's team
    start_time : datetime
        start time of the lap
    stop_time : datetime
        finish time of the lap
    best_lap : timedelta
        time of the best lap

    Methods
    -------
    statistics : str
        Returns the pretty string with the driver's statistics
    """

    def __init__(self, abbr=None, name=None, team=None, start_time=None, stop_time=None,
                 best_lap=None):
        self.abbr = abbr
        self.name = name
        self.team = team
        self.start_time = start_time
        self.stop_time = stop_time
        self.best_lap = best_lap

    def __repr__(self):
        return f'Driver ({self.__dict__})'

    def statistics(self):
        return '{:<20} | {:<25} | {}'.format(self.name, self.team, str(self.best_lap)[:-3])

    def get_start_time(self, data_path=DATA_PATH):
        """Parse and calc start, stop and best lap times for a particular driver.
        Replaces 'parse_logs' function used for parsing all drivers at once"""
        with open(os.path.join(data_path, START_LOG_FILE), 'r', encoding='UTF-8') as f:
            lines = [line for line in f if line.strip()]
            for line in lines:
                abbr, start_time = line[:3], line.split('_')[1].rstrip()
                if self.abbr == abbr:
                    self.start_time = dt.datetime.strptime(start_time, "%H:%M:%S.%f")
                    break

    def get_stop_time(self, data_path=DATA_PATH):
        with open(os.path.join(data_path, END_LOG_FILE), 'r', encoding='UTF-8') as f:
            lines = [line for line in f if line.strip()]
            for line in lines:
                abbr, stop_time = line[:3], line.split('_')[1].rstrip()
                if self.abbr == abbr:
                    self.stop_time = dt.datetime.strptime(stop_time, "%H:%M:%S.%f")
                    break

    def get_best_lap_time(self):
        if self.start_time > self.stop_time:
            self.start_time, self.stop_time = self.stop_time, self.start_time
        self.best_lap = self.stop_time - self.start_time


def drivers_from_abbr(data_path):
    """
    Return the list of driver instances each with their name, abbreviation and team parsed from the
    data_path/ABBR_FILE
    """
    drivers = []
    with open(os.path.join(data_path, ABBR_FILE), 'r', encoding='UTF-8') as f:
        for line in f:
            abbr, name, team = line.split('_')
            new_driver = Driver(abbr=abbr, name=name, team=team.rstrip())
            drivers.append(new_driver)
    return drivers


def parse_logs(data_path, drivers):
    """
    Modify the passed drivers list in-place: update each with the start and finish times from the parsing of the logs
    in data_path
    """
    with open(os.path.join(data_path, START_LOG_FILE), 'r', encoding='UTF-8') as f:
        # use only non-blank lines
        lines = (line for line in f if line.strip())
        for line in lines:
            abbr, start_time = line[:3], line.split('_')[1].rstrip()
            for driver in drivers:
                if driver.abbr == abbr:
                    driver.start_time = dt.datetime.strptime(start_time, "%H:%M:%S.%f")
                    break
    with open(os.path.join(data_path, END_LOG_FILE), 'r', encoding='UTF-8') as f:
        # use only non-blank lines
        lines = (line for line in f if line.strip())
        for line in lines:
            abbr, stop_time = line[:3], line.split('_')[1].rstrip()
            for driver in drivers:
                if driver.abbr == abbr:
                    driver.stop_time = dt.datetime.strptime(stop_time, "%H:%M:%S.%f")
                    break


def build_report(drivers, data_path=DATA_PATH):
    """
    Build the report based on files of name abbreviations and time logs in DATA_PATH. Calculate the best lap time for
    each driver. Return the list of drivers.
    """
    parse_logs(data_path, drivers)
    for driver in drivers:
        if driver.start_time > driver.stop_time:
            driver.start_time, driver.stop_time = driver.stop_time, driver.start_time
        driver.best_lap = driver.stop_time - driver.start_time
    return drivers


def print_report(drivers, asc=True, driver=None):
    """
    Return str report based on the report of the build_report function.

    Parameters:
    drivers - the list of drivers each with their info as properties
    asc - ascending order if True
    driver - if set, print the report of this only driver
    """
    if driver:
        for d in drivers:
            if driver.lower() in d.name.lower() or driver.lower() in d.abbr.lower():
                return d.statistics()
        else:
            return 'Driver not found'
    else:
        sorted_drivers = sorted(drivers, key=lambda dr: dr.best_lap)
        res_table = ['{:2d}. '.format(i + 1) + driver.statistics() for i, driver in enumerate(sorted_drivers)]
        if asc:
            res_table.insert(15, '-' * 60)
        else:
            res_table.reverse()
        report = '\n'.join(res_table)
        return report


@app.route('/report')
def common_report():
    """Show common statistics of all drivers"""
    asc_order = False if request.args.get('order') == 'desc' else True
    drivers = drivers_from_abbr(DATA_PATH)
    return print_report(build_report(drivers), asc_order, None)


@app.route('/drivers')
def list_drivers():
    drivers = drivers_from_abbr(DATA_PATH)
    req_driver = request.args.get('driver_id')

    if req_driver:
        for driver in drivers:
            if driver.abbr == req_driver:
                driver.get_start_time()
                driver.get_stop_time()
                driver.get_best_lap_time()
                return driver.statistics()
        else:
            return 'driver not found'
    else:

        desc_order = True if request.args.get('order') == 'desc' else False
        drivers.sort(key=lambda d: d.name, reverse=desc_order)
        return '<br>'.join(driver.name + ' ' + driver.abbr for driver in drivers)


if __name__ == '__main__':
    app.run()
