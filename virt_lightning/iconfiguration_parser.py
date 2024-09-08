from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
)


#
# Интерфейс для получения конфигурации из различных источников
#
class IConfigurationParser(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, uri):
        pass

    @abstractproperty
    def backend(self):
        pass

    @abstractproperty
    def network(self):
        pass

    @abstractproperty
    def user(self):
        pass

    @abstractproperty
    def registry(self):
        pass

    def __repr__(self):
        return f"ConfigurationSource({self.uri})"
