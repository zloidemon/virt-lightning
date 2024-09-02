from virt_lightning.iconfiguration import IConfigurationRegistry


class ConfigurationRegistry(IConfigurationRegistry):
    def __init__(self):
        self.__entrypoint = None

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

    def __eq__(self, other):
        return self.entrypoint == other.entrypoint
