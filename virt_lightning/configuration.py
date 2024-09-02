import pathlib
import tomllib

from virt_lightning import consts
from virt_lightning.configuration_backend import ConfigurationBackend
from virt_lightning.configuration_login_ssh import ConfigurationLoginSSH
from virt_lightning.configuration_posix_user import ConfigurationPosixUser
from virt_lightning.configuration_registry import ConfigurationRegistry
from virt_lightning.configuration_tcpip import ConfigurationTCPIP
from virt_lightning.iconfiguration import (
    IConfigurationBuilder,
    IConfigurationSource,
)


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
        tcpip = ConfigurationTCPIP()
        tcpip.name = self.__get("network_name")
        tcpip.cidr = self.__get("network_cidr")
        tcpip.auto_cleanup = self.__get("network_auto_clean_up")

        return tcpip

    @property
    def backend(self):
        config = ConfigurationBackend()
        config.entrypoint = self.__get("libvirt_uri")
        config.storage = self.__get("storage_pool")

        return config

    @property
    def user(self):
        ssh_login = ConfigurationLoginSSH()
        ssh_login.key = pathlib.PosixPath(self.__get("ssh_key_file"))

        config_user = ConfigurationPosixUser()
        config_user.username = consts.DEFAULT_USER_USERNAME
        config_user.password = self.__get("root_password")

        config_user.login = ssh_login
        return config_user

    @property
    def registry(self):
        registries = []

        for entrypoint in self.__get("registry_urls").split(","):
            if entrypoint and entrypoint != "":
                _registry = ConfigurationRegistry()
                _registry.entrypoint = entrypoint
                registries.append(_registry)

        #
        # NOTE: Добавление адреса к хранилищу образов по-умолчанию в конец
        #
        path = (
            consts.DEFAULT_BASE_REGISTRY_URL + "/v2/library/{resource}/blobs/{hashsum}"
        )

        _registry = ConfigurationRegistry()
        _registry.entrypoint = path

        registries.append(_registry)

        return registries


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
