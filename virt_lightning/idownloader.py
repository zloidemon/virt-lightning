from abc import (
    ABCMeta,
    abstractmethod,
)


#
# Общий интерфейс получения образов
#
class IDownloader(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, configuration, storage_dir):
        pass

    @abstractmethod
    def pull(self, **kwargs):
        pass
