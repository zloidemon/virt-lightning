from virt_lightning.iconfiguration import IConfigurationPosixUser


class ConfigurationPosixUser(IConfigurationPosixUser):
    #
    # NOTE: В login на самом деле стоит сделать не только SSH, а и другое
    #       либо несколько, используя список
    #
    def __init__(self, username, password, login):
        self.__username = username
        self.__password = password
        self.__login = login

    @property
    def uid(self):
        return None

    @property
    def gid(self):
        return None

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def login(self):
        return self.__login
