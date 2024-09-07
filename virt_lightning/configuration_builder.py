import tomllib
from pathlib import PosixPath
from urllib.parse import ParseResult

from virt_lightning.iconfiguration import IConfigurationBuilder
from virt_lightning.configuration_load_file import ConfigurationLoadFile


class ConfigurationBuilder(IConfigurationBuilder):
    def __init__(self, parser):
        self.__parser = parser

        self.__source = None
        self.__configuration = None

    @classmethod
    def create(cls, parser):
        return cls(parser)

    def set_source(self, source):
        if self.__source:
            raise KeyError("source already setup")

        self.__source = source

        if not isinstance(source, ParseResult):
            raise TypeError("source must be ParseResult type")

        match (source.scheme, source.netloc):
            case "", "":
                path = PosixPath(source.geturl())
                self.__reader = ConfigurationLoadFile(path)
            case "http" | "https", _:
                raise NotImplementedError(f"HTTP: {source.scheme} not supported")
            case _:
                raise NotImplementedError(f"source: {source.scheme} not supported")

        return self

    def set_configuration(self, obj):
        self.__configuration = obj
        return self

    def build(self):
        if self.__source is None:
            raise ValueError("source must be defined before build")

        if self.__configuration is None:
            raise ValueError("configuration class must be defined before build")

        self.__format, data = self.__reader.read()

        match self.__format:
            case "toml":
                parsed_data = self.__parser(tomllib.loads(data))
            case _:
                raise KeyError(f"unknown format: {self.__format}")

        return self.__configuration(parsed_data)


class Configuration:
    def __init__(self, source):
        self.backend = source.backend
        self.network = source.network
        self.user = source.user
        self.registry = source.registry

    def __repr__(self):
        return "Configuration()"
