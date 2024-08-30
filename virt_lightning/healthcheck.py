from virt_lightning.ihealthcheck import IHealthcheck


class Healthcheck(IHealthcheck):
    def __init__(self, cmd, configuration):
        self.__cmd = cmd
        self.__configuration = configuration

    @property
    def command(self):
        return self.__cmd

    @property
    def configuration(self):
        return self.__configuration

    def __eq__(self, other):
        if self.command != other.command:
            return False
        return self.configuration != other.configuration
