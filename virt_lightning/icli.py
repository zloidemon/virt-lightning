from abc import (
    ABCMeta,
    abstractmethod,
)


#
# Интерфейс команд для командной строки
#
class ICLIcmd(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, action_subparsers, parent_parser):
        pass

    @abstractmethod
    def arguments(self):
        pass

    @abstractmethod
    def context(self, args):
        pass

    @staticmethod
    @abstractmethod
    def run(*args, **kwargs):
        pass
