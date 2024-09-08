from abc import (
    ABCMeta,
    abstractmethod,
)


#
# Интерфейс для подготовки объекта с данными для создания объекта с
# конфигурацией
#
class IConfigurationParser(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def parse(cls, config):
        pass

    def __repr__(self):
        return "ConfigurationParser()"
