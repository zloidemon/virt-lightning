from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
)


#
# Общий интерфейс проверки доступности
#
class IHealthcheck(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, cmd, configuration):
        pass

    @abstractproperty
    def command(self):
        pass

    @abstractproperty
    def configuration(self):
        pass

    def __repr__(self):
        return f"Healthcheck(command={self.command})"
