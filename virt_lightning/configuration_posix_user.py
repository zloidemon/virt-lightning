from virt_lightning.iconfiguration import IConfigurationPosixUser


class ConfigurationPosixUser(IConfigurationPosixUser):
    #
    # NOTE: В login на самом деле стоит сделать не только SSH, а и другое
    #       либо несколько, используя список. Стоит глянуть POSIX документацию
    #       и правильно сделать gid/uid, так как есть real, effective и прочие.
    #
    def __init__(self):
        self.__username = None
        self.__groupname = None
        self.__password = None
        self.__login = None
        self.__uid = None
        self.__gid = None

    @property
    def uid(self):
        if self.__uid is None:
            raise TypeError("uid must be set integer value")
        return self.__uid

    @uid.setter
    def uid(self, value):
        if not isinstance(value, int):
            raise TypeError("uid must be integer value")

        if value < 0:
            raise ValueError("uid must be positive integer")

        self.__uid = value

    @property
    def gid(self):
        if self.__gid is None:
            raise TypeError("gid must be set integer value")
        return self.__gid

    @gid.setter
    def gid(self, value):
        if not isinstance(value, int):
            raise TypeError("gid must be integer value")

        if value < 0:
            raise ValueError("gid must be positive integer")

        self.__gid = value

    @property
    def username(self):
        if self.__username is None:
            raise TypeError("username must be set string value")
        return self.__username

    @username.setter
    def username(self, value):
        if not isinstance(value, str):
            raise TypeError("username must be string value")
        if len(value) < 1 or value == "":
            raise ValueError("username can not be empty")
        self.__username = value

    @property
    def groupname(self):
        if self.__groupname is None:
            raise TypeError("groupname must be set string value")
        return self.__groupname

    @groupname.setter
    def groupname(self, value):
        if not isinstance(value, str):
            raise TypeError("groupname must be string value")
        if len(value) < 1 or value == "":
            raise ValueError("groupname can not be empty")
        self.__groupname = value

    @property
    def password(self):
        if self.__password is None:
            raise TypeError("password must be set string value")
        return self.__password

    @password.setter
    def password(self, value):
        if not isinstance(value, str):
            raise TypeError("password must be string value")
        if len(value) < 1 or value == "":
            raise ValueError("password can not be empty")
        self.__password = value

    #
    # FIXME: Убрать login куда-то в другое место. Лучше использовать как один из
    #        вариантов методов авторизации
    #
    @property
    def login(self):
        return self.__login

    @login.setter
    def login(self, value):
        self.__login = value
