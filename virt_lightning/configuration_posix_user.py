from virt_lightning.iconfiguration import IConfigurationPosixUser


class ConfigurationPosixUser(IConfigurationPosixUser):
    #
    # NOTE: В login на самом деле стоит сделать не только SSH, а и другое
    #       либо несколько, используя список. Стоит глянуть POSIX документацию
    #       и правильно сделать gid/uid, так как есть real, effective и прочие.
    #
    def __init__(self, username, password, login):
        self.__username = username
        self.__password = password
        self.__login = login
        self.__uid = None
        self.__gid = None

    @uid.setter
    def uid(self, value):
        if not isinstance(value, int):
            raise TypeError("uid must be integer value")

        if value < 0:
            raise ValueError("uid must be positive integer")

        self.__uid = value

    @property
    def uid(self):
        if not self.__uid:
            raise TypeError("uid must be set integer value")
        return self.__uid

    @gid.setter
    def gid(self, value):
        if not isinstance(value, int):
            raise TypeError("gid must be integer value")

        if value < 0:
            raise ValueError("gid must be positive integer")

        self.__gid = value

    @property
    def gid(self):
        if not self.__gid:
            raise TypeError("gid must be set integer value")
        return self.__gid

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def login(self):
        return self.__login
