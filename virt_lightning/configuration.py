import pathlib

import tomllib

from virt_lightning import consts
from virt_lightning.iconfiguration import (
    IConfigurationBackend,
    IConfigurationBuilder,
    IConfigurationLogin,
    IConfigurationNetworkModel,
    IConfigurationRegistry,
    IConfigurationSource,
    IConfigurationUnixUser,
)


class ConfigurationBackend(IConfigurationBackend):
    def __init__(self, uri, storage):
        self.__entrypoint = uri
        self.__storage = storage

    @property
    def entrypoint(self):
        return self.__entrypoint

    @property
    def storage(self):
        return self.__storage


class ConfigurationTCPIP(IConfigurationNetworkModel):
    def __init__(self, name, cidr, clean):
        self.__name = name
        self.__cidr = cidr
        self.__clean = clean

    @property
    def name(self):
        return self.__name

    @property
    def cidr(self):
        return self.__cidr

    @property
    def auto_cleanup(self):
        return self.__clean

    def __repr__(self):
        return f"ConfigurationTCPIP({self.name},{self.cidr},{self.auto_cleanup})"


class ConfigurationLoadFile(IConfigurationSource):
    def __init__(self, filename=None):
        self.__filename = filename
        self.__cached = None
        self.__config = {}
        self.__section = "main"
        self.__config[self.__section] = consts.DEFAULT_CONFIGURATION[self.__section]

        #
        # FIXME: Переделать на получение данных, и убрать чтение из фалов
        #        в данном классе. Например передать в конструктор поток байт.
        #
        if self.__filename:
            self.__refresh()

    def __get(self, key):
        return self.__config[self.__section].get(key)

    def __refresh(self):
        if not self.__cached and self.__filename.expanduser().exists():
            self.__cached = self.__filename.expanduser().read_text()
        if self.__cached:
            config = tomllib.loads(self.__cached)
            self.__config[self.__section].update(config[self.__section])

    @property
    def uri(self):
        return self.__filename

    @property
    def network(self):
        return ConfigurationTCPIP(
            self.__get("network_name"),
            self.__get("network_cidr"),
            self.__get("network_auto_clean_up"),
        )

    @property
    def backend(self):
        return ConfigurationBackend(
            self.__get("libvirt_uri"),
            self.__get("storage_pool"),
        )

    @property
    def user(self):
        return ConfigurationUnixUser(
            consts.DEFAULT_USER_USERNAME,
            self.__get("root_password"),
            ConfigurationLoginSSH(self.__get("ssh_key_file")),
        )

    @property
    def registry(self):
        registries = []

        for registry in self.__get("registry_urls").split(","):
            if registry and registry != "":
                registries.append(ConfigurationRegistry(registry))

        #
        # NOTE: Добавление адреса к хранилищу образов по-умолчанию в конец
        #
        path = (
            consts.DEFAULT_BASE_REGISTRY_URL + "/v2/library/{resource}/blobs/{hashsum}"
        )
        registries.append(ConfigurationRegistry(path))

        return registries


class ConfigurationLoginSSH(IConfigurationLogin):
    def __init__(self, filename):
        self.__filename = filename

    @property
    def method(self):
        return consts.LoginMethod.SSH

    @property
    def key(self):
        return self.__filename


class ConfigurationUnixUser(IConfigurationUnixUser):
    #
    # NOTE: В login на самом деле стоит сделать не только SSH, а и другое
    #       либо несколько, используя список
    #
    def __init__(self, username, password, login):
        self.__username = username
        self.__password = password
        self.__login = login

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def login(self):
        return self.__login


class ConfigurationRegistry(IConfigurationRegistry):
    def __init__(self, entrypoint):
        self.__entrypoint = entrypoint

    @property
    def entrypoint(self):
        return self.__entrypoint


class ConfigurationBuilder(IConfigurationBuilder):
    def __init__(self):
        self.__source = None

    @classmethod
    def create(cls):
        return cls()

    def set_source(self, source):
        if self.__source:
            raise Exception("source already setup")
        else:
            self.__source = source
        return self

    def build(self):
        if not self.__source:
            raise Exception("source must be defined before build")

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


class ProxyLegacyConfiguration:
    def __init__(self, source=None):
        builder = ConfigurationBuilder.create()

        #
        # NOTE: Добавить поддержку загрузки конфигурации например по HTTP
        #
        if not source:
            builder.set_source(ConfigurationLoadFile())
        elif source and source.scheme == "" and source.netloc == "":
            filename = pathlib.PosixPath(source.geturl())
            builder.set_source(ConfigurationLoadFile(filename))

        self.data = builder.build()

    @property
    def libvirt_uri(self):
        return self.data.backend.entrypoint

    @property
    def network_name(self):
        return self.data.network.name

    @property
    def network_cidr(self):
        return self.data.network.cidr

    @property
    def network_auto_clean_up(self):
        return self.data.network.auto_cleanup

    @property
    def root_password(self):
        return self.data.user.password

    @property
    def ssh_key_file(self):
        return self.data.user.login.key

    @property
    def storage_pool(self):
        return self.data.backend.storage

    @property
    def registry_urls(self):
        return self.data.registry
