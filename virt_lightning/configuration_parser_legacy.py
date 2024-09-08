from pathlib import PosixPath

from virt_lightning import consts
from virt_lightning.configuration_backend import ConfigurationBackend
from virt_lightning.configuration_login_ssh import ConfigurationLoginSSH
from virt_lightning.configuration_posix_user import ConfigurationPosixUser
from virt_lightning.configuration_registry import ConfigurationRegistry
from virt_lightning.configuration_tcpip import ConfigurationTCPIP
from virt_lightning.iconfiguration_parser import IConfigurationParser


class ConfigurationParserLegacy(IConfigurationParser):
    def __init__(self, config, section):
        self.__config = config
        self.__section = section

    @classmethod
    def parse(cls, config):
        _section = "main"
        _config = {
            _section: consts.DEFAULT_CONFIGURATION[_section],
        }

        if config.get(_section):
            _config[_section].update(config[_section])

        return cls(_config, _section)

    def __get(self, key):
        return self.__config[self.__section].get(key)

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
        ssh_login.key = PosixPath(self.__get("ssh_key_file"))

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
