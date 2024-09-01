from virt_lightning.iconfiguration import IConfigurationHealthcheck


class ConfigurationHealthcheck(IConfigurationHealthcheck):
    def __init__(self):
        self.__interval = 30
        self.__timeout = 30
        self.__start_period = 0
        self.__start_interval = 5
        self.__retries = 3

    @property
    def interval(self):
        return self.__interval

    @interval.setter
    def interval(self, value):
        if value < 1:
            raise ValueError("interval must be greater than zero")

        self.__interval = value

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        if value < 1:
            raise ValueError("timeout must be greater than zero")

        self.__timeout = value

    @property
    def start_period(self):
        return self.__start_period

    @start_period.setter
    def start_period(self, value):
        if value < 0:
            raise ValueError("start_period must be positive")

        self.__start_period = value

    @property
    def start_interval(self):
        return self.__start_interval

    @start_interval.setter
    def start_interval(self, value):
        if value < 0:
            raise ValueError("start_interval must be positive")

        self.__start_interval = value

    @property
    def retries(self):
        return self.__retries

    @retries.setter
    def retries(self, value):
        if value < 1:
            raise ValueError("retries must be greater than zero")

        self.__retries = value

    def __eq__(self, other):
        if self.interval != other.interval:
            return False
        if self.timeout != other.timeout:
            return False
        if self.start_period != other.start_period:
            return False
        if self.start_interval != other.start_interval:
            return False
        return self.retries == other.retries
