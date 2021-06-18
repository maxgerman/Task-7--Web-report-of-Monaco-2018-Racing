import os
import datetime as dt

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

    driver_list = []

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

    def _drivers_from_abbr(data_path: str = DATA_PATH, abbr_file=ABBR_FILE) -> list:
        """
        Return the list of driver instances each with their name, abbreviation and team parsed from the
        data_path/ABBR_FILE
        """
        drivers = []
        with open(os.path.join(data_path, abbr_file), 'r', encoding='UTF-8') as f:
            for line in f:
                abbr, name, team = line.split('_')
                new_driver = Driver(abbr=abbr, name=name, team=team.rstrip())
                drivers.append(new_driver)
        return drivers


    @staticmethod
    def _parse_logs(drivers: list, data_path: str = DATA_PATH) -> list:
        """
        Return the copy of drivers list with updated start and finish times from the parsing of the logs
        in 'data_path'
        """
        result_drivers = drivers[:]
        with open(os.path.join(data_path, START_LOG_FILE), 'r', encoding='UTF-8') as f:
            lines = (line for line in f if line.strip())
            for line in lines:
                abbr, start_time = line[:3], line.split('_')[1].rstrip()
                for driver in result_drivers:
                    if driver.abbr == abbr:
                        driver.start_time = dt.datetime.strptime(start_time, "%H:%M:%S.%f")
                        break
        with open(os.path.join(data_path, END_LOG_FILE), 'r', encoding='UTF-8') as f:
            lines = (line for line in f if line.strip())
            for line in lines:
                abbr, stop_time = line[:3], line.split('_')[1].rstrip()
                for driver in result_drivers:
                    if driver.abbr == abbr:
                        driver.stop_time = dt.datetime.strptime(stop_time, "%H:%M:%S.%f")
                        break
        return result_drivers

    @staticmethod
    def build_report(data_path: str = DATA_PATH, abbr_file: str = ABBR_FILE) -> list:
        """
        Build the report based on files of name abbreviations and time logs in DATA_PATH. Calculate the best lap time for
        each driver. Return the list of drivers.
        """
        drivers = Driver._drivers_from_abbr(data_path, abbr_file)
        drivers = Driver._parse_logs(drivers, data_path)
        for driver in drivers:
            if driver.start_time > driver.stop_time:
                driver.start_time, driver.stop_time = driver.stop_time, driver.start_time
            driver.best_lap = driver.stop_time - driver.start_time
        Driver.driver_list = drivers
        return drivers

    @staticmethod
    def _print_report(asc: bool = True, driver_query: str = None) -> str:
        """
        Pretty print the report of drivers statistics.
        Sorted by best lap time.
        Optionally, search for only one driver by name or abbr.


        Parameters:
        drivers - list of drivers built by 'build_report' function.
        asc - ascending order if True
        driver_query - if set, print the report of this only driver
        """

        if driver_query:
            for d in Driver.driver_list:
                if driver_query.lower() in d.name.lower() or driver_query.lower() in d.abbr.lower():
                    return d.statistics()
            else:
                return 'Driver not found'
        else:
            sorted_drivers = sorted(Driver.driver_list, key=lambda dr: dr.best_lap)
            res_table = ['{:2d}. '.format(i + 1) + driver.statistics() for i, driver in enumerate(sorted_drivers)]
            if asc:
                res_table.insert(15, '-' * 60)
            else:
                res_table.reverse()
            report = '\n'.join(res_table)
            return report

    @staticmethod
    def all(asc=True):
        return Driver._print_report(asc=asc)

    @staticmethod
    def get(driver_id):
        return Driver._print_report(driver_query=driver_id)
