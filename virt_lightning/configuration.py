from configparser import ConfigParser

from virt_lightning.consts import LoginMethod
from virt_lightning.iconfiguration import (
    IConfigurationBackend,
    IConfigurationBuilder,
    IConfigurationLogin,
    IConfigurationNetworkModel,
    IConfigurationSource,
    IConfigurationUnixUser,
)

DEFAULT_CONFIGURATION = {
    "main": {
        "libvirt_uri": "qemu:///system",
        "root_password": "root",
        "storage_pool": "virt-lightning",
        "network_name": "virt-lightning",
        "network_cidr": "192.168.123.0/24",
        "network_auto_clean_up": True,
        "ssh_key_file": "~/.ssh/id_rsa.pub",
        "private_hub": "",
    }
}


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
    def __init__(self, filename):
        self.__filename = filename
        self.__cached = None
        self.__config = ConfigParser()
        self.__section = "main"
        self.__config[self.__section] = DEFAULT_CONFIGURATION[self.__section]

        self.__refresh()

    def __get(self, key):
        return self.__config.get(self.__section, key)

    def __refresh(self):
        if not self.__cached and self.__filename.expanduser().exists():
            self.__cached = self.__filename.expanduser().read_text()
        return self.__config.read_string(self.__cached)

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
            "root",
            self.__get("root_password"),
            ConfigurationLoginSSH(self.__get("ssh_key_file")),
        )


class ConfigurationLoginSSH(IConfigurationLogin):
    def __init__(self, filename):
        self.__filename = filename

    @property
    def method(self):
        return LoginMethod.SSH

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
        )


class Configuration:
    def __init__(self, backend, user, network):
        self.backend = backend
        self.network = network
        self.user = user

    def __repr__(self):
        return "Configuration()"


class ProxyLegacyConfiguration:
    def __init__(self, filename=None):
        builder = ConfigurationBuilder.create().set_source(
            ConfigurationLoadFile(filename)
        )

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

    #
    # FIXME: Переделать на использование множества источников из конфигурации
    #
    @property
    def private_hub(self):
        return [x for x in self.__get("private_hub").split(",") if x != ""]
