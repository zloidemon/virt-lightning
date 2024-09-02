from virt_lightning.iconfiguration import IConfigurationNetworkModel


class ConfigurationTCPIP(IConfigurationNetworkModel):
    def __init__(self):
        self.__name = None
        self.__cidr = None
        self.__clean = None

    @property
    def name(self):
        if not isinstance(self.__name, str):
            raise AttributeError("name must be set before use")
        return self.__name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("name must be string")
        self.__name = value

    @property
    def cidr(self):
        if not isinstance(self.__cidr, str):
            raise AttributeError("cidr must be set before use")
        return self.__cidr

    @cidr.setter
    def cidr(self, value):
        if not isinstance(value, str):
            raise TypeError("cidr must be string")
        self.__cidr = value

    @property
    def auto_cleanup(self):
        if not isinstance(self.__clean, bool):
            raise AttributeError("auto_cleanup must be set before use")
        return self.__clean

    @auto_cleanup.setter
    def auto_cleanup(self, value):
        if not isinstance(value, bool):
            raise TypeError("auto_cleanup must be boolean")
        self.__clean = value

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.cidr != other.cidr:
            return False
        return self.auto_cleanup == other.auto_cleanup

    def __repr__(self):
        return f"ConfigurationTCPIP({self.name},{self.cidr},{self.auto_cleanup})"
