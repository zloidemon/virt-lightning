from abc import (
    ABCMeta,
    abstractproperty,
)


#
# Интерфейс конфигурации приложения
#
class IConfigurationApplication(metaclass=ABCMeta):
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
