import json
from abc import (
    ABCMeta,
    abstractmethod,
)


#
# Интерфейс для преобразования в jsonb
#
class IJsonb(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add(self, path, value):
        pass

    @abstractmethod
    def remove(self, path):
        pass

    @abstractmethod
    def replace(self, path, value):
        pass

    @abstractmethod
    def copy(self, from_path, path):
        pass

    @abstractmethod
    def move(self, from_path, path):
        pass

    @abstractmethod
    def test(self, path, value):
        pass

    def __str__(self):
        return json.dumps(self._operations)
