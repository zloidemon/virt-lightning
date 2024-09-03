from virt_lightning.iconfiguration import IConfigurationBuilder


class ConfigurationBuilder(IConfigurationBuilder):
    def __init__(self):
        self.__source = None

    @classmethod
    def create(cls):
        return cls()

    def set_source(self, source):
        if self.__source:
            raise KeyError("source already setup")
        else:
            self.__source = source
        return self

    def build(self):
        if not self.__source:
            raise ValueError("source must be defined before build")

        return Configuration(
            self.__source.backend,
            self.__source.user,
            self.__source.network,
            self.__source.registry,
        )


class Configuration:
    def __init__(self, backend, user, network, registry):
        self.backend = backend
        self.network = network
        self.user = user
        self.registry = registry

    def __repr__(self):
        return "Configuration()"
