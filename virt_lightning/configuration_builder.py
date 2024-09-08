import tomllib
from pathlib import PosixPath
from urllib.parse import ParseResult

from virt_lightning.iconfiguration import IConfigurationBuilder
from virt_lightning.configuration_load_file import ConfigurationLoadFile


class ConfigurationBuilder(IConfigurationBuilder):
    def __init__(self):
        self.__parser = None
        self.__source = None

    @classmethod
    def create(cls):
        return cls()

    def set_parser(self, parser):
        self.__parser = parser
        return self

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

    def build(self, config):
        if self.__source is None:
            raise ValueError("source must be defined before build")

        if config is None:
            raise ValueError("configuration class must be defined before build")

        self.__format, data = self.__reader.read()

        match self.__format:
            case "toml":
                parsed_data = self.__parser(tomllib.loads(data))
            case _:
                raise KeyError(f"unknown format: {self.__format}")

        return config(parsed_data)


class Configuration:
    def __init__(self, source):
        self.backend = source.backend
        self.network = source.network
        self.user = source.user
        self.registry = source.registry

    def __repr__(self):
        return "Configuration()"
