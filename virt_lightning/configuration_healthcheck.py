from virt_lightning.iconfiguration import IConfigurationHealthcheck


class ConfigurationHealthcheck(IConfigurationHealthcheck):
    def __init__(self, interval, timeout, start_period, start_interval, retries):
        self.__interval = interval
        self.__timeout = timeout
        self.__start_period = start_period
        self.__start_interval = start_interval
        self.__retries = retries

    @property
    def interval(self):
        return self.__interval

    @property
    def timeout(self):
        return self.__timeout

    @property
    def start_period(self):
        return self.__start_period

    @property
    def start_interval(self):
        return self.__start_interval

    @property
    def retries(self):
        return self.__retries

    def __eq__(self, other):
        if self.interval != other.interval:
            return False
        if self.timeout != other.timeout:
            return False
        if self.start_period != other.start_period:
            return False
        if self.start_interval != other.start_interval:
            return False
        if self.retries != other.retries:
            return False
        return True
