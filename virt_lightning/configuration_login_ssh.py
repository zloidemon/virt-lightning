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
        if self.__filename is None:
            raise TypeError("key must be set before access")

        return self.__filename

    @key.setter
    def key(self, value):
        if not isinstance(value, PosixPath):
            raise TypeError("key must be PosixPath")

        value = value.expanduser()

        if not value.exists():
            raise ValueError(f"key '{value}' not found")

        if not value.is_file():
            raise ValueError(f"key '{value}' is not file")

        #
        # FIXME: Добавить провервку ключей в зависимости от алгоритма
        #

        self.__filename = value

    def __eq__(self, other):
        if self.method != other.method:
            return False
        return self.key == other.key
