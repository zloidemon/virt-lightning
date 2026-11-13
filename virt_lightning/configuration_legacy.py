import logging

logger = logging.getLogger("virt_lightning")

#
# Класс для сохранения совместимости доступа к конфигурации для старого кода
#
class LegacyConfiguration:
    def __init__(self, data):
        self.data = data

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
        if self.__get("ssh_key_file"):
            return self.__get("ssh_key_file")

        found = next((Path.home() / ".ssh").glob("id_*.pub"), None)
        logger.debug(f"No SSH key defined in configuration, failing back on {found}")

        return found

    @property
    def storage_pool(self):
        return self.data.backend.storage

    @property
    def registry_urls(self):
        return self.data.registry
