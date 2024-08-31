from virt_lightning.iconfiguration import IConfigurationPosixUser


class ConfigurationPosixUser(IConfigurationPosixUser):
    #
    # NOTE: В login на самом деле стоит сделать не только SSH, а и другое
    #       либо несколько, используя список. Стоит глянуть POSIX документацию
    #       и правильно сделать gid/uid, так как есть real, effective и прочие.
    #
    def __init__(self, username, password, login, uid=None, gid=None):
        self.__username = username
        self.__password = password
        self.__login = login
        self.__uid = uid
        self.__gid = gid

    @property
    def uid(self):
        return self.__uid

    @property
    def gid(self):
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
