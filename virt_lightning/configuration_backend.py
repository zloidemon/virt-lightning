from virt_lightning.iconfiguration import IConfigurationBackend


class ConfigurationBackend(IConfigurationBackend):
    def __init__(self):
        self.__entrypoint = None
        self.__storage = None

    @property
    def entrypoint(self):
        if not isinstance(self.__entrypoint, str):
            raise AttributeError("entrypoint must be set before use")
        return self.__entrypoint

    @entrypoint.setter
    def entrypoint(self, value):
        if not isinstance(value, str):
            raise TypeError("entrypoint must be string")
        self.__entrypoint = value

    @property
    def storage(self):
        if not isinstance(self.__storage, str):
            raise AttributeError("storage must be set before use")
        return self.__storage

    @storage.setter
    def storage(self, value):
        if not isinstance(value, str):
            raise TypeError("sotrage must be string")
        self.__storage = value

    def __eq__(self, other):
        if self.entrypoint != other.entrypoint:
            return False
        return self.storage == other.storage
