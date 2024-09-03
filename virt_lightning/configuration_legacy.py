from pathlib import PosixPath
from urllib.parse import ParseResult

from virt_lightning.configuration_builder import ConfigurationBuilder
from virt_lightning.configuration_load_file import ConfigurationLegacyLoadFile


class ProxyLegacyConfiguration:
    def __init__(self, data):
        self.data = data

    @classmethod
    def load(cls, source=None):
        builder = ConfigurationBuilder.create()
        config = ConfigurationLegacyLoadFile()

        #
        # NOTE: Добавить поддержку загрузки конфигурации например по HTTP
        #
        if not source:
            builder.set_source(config)
        else:
            if not isinstance(source, ParseResult):
                raise TypeError("source must be ParseResult type")
            match (source.scheme, source.netloc):
                case "", "":
                    config.load_from(PosixPath(source.geturl()))
                    builder.set_source(config)
                case _:
                    raise NotImplementedError(f"source: {source.scheme} supported")

        return cls(builder.build())

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
