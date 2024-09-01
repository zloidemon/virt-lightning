from pathlib import PosixPath
from virt_lightning import consts

from virt_lightning.iconfiguration import IConfigurationLogin


class ConfigurationLoginSSH(IConfigurationLogin):
    def __init__(self):
        self.__filename = None

    @property
    def method(self):
        return consts.LoginMethod.SSH

    @property
    def key(self):
        return self.__filename

    @key.setter
    def key(self, value):
        if not isinstance(volume, PosixPath):
            raise TypeError("key must be PosixPath")

        #
        # FIXME: Добавить провервку ключей в зависимости от алгоритма
        #
        if value == "":
            raise ValueError("key can not be empty")

        if not value.exists() or not value.is_file():
            raise ValueError(f"key '{value}' not found")

        self.__filename = value

    def __eq__(self, other):
        if self.method != other.method:
            return False
        return self.key == other.key
