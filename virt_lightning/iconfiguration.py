from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
)


#
# Общий интерфейс для сетевых моделей
#
class IConfigurationNetworkModel(metaclass=ABCMeta):
    @abstractproperty
    def name(self):
        pass


#
# Интерфейс для получения конфигурации из различных источников
#
class IConfigurationSource(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, uri):
        pass

    @abstractproperty
    def backend(self):
        pass

    @abstractproperty
    def network(self):
        pass

    @abstractproperty
    def user(self):
        pass

    @abstractproperty
    def registry(self):
        pass

    @abstractproperty
    def uri(self):
        pass

    def __repr__(self):
        return f"ConfigurationSource({self.uri})"


#
# Пользователь с параметрами для POSIX
#
class IConfigurationPosixUser(metaclass=ABCMeta):
    @abstractproperty
    def uid(self):
        pass

    @abstractproperty
    def gid(self):
        pass

    @abstractproperty
    def username(self):
        pass

    @abstractproperty
    def password(self):
        pass

    @abstractmethod
    def login(self):
        pass

    def __repr__(self):
        return f"ConfigurationUnixUser({self.username})"


#
# Общий метод для входа входа в системы
#
class IConfigurationLogin(metaclass=ABCMeta):
    @abstractproperty
    def method(self):
        pass


#
# Интерфейс стротеля конфигураций
#
class IConfigurationBuilder(metaclass=ABCMeta):
    @abstractmethod
    def set_source(self, source):
        pass

    @classmethod
    @abstractmethod
    def create(cls):
        pass

    @abstractmethod
    def build(self):
        pass


#
# Интерфейс для бэкендов
#
class IConfigurationBackend(metaclass=ABCMeta):
    @abstractproperty
    def entrypoint(self):
        pass

    @abstractproperty
    def storage(self):
        pass


#
# Интерфейс источников образов
#
class IConfigurationRegistry(metaclass=ABCMeta):
    @abstractproperty
    def entrypoint(self):
        pass

    def __repr__(self):
        return f"ConfigurationRegistry({self.entrypoint})"


#
# Интерфейс конфигурации для проверок доступности
#
class IConfigurationHealthcheck(metaclass=ABCMeta):
    @abstractproperty
    def interval(self):
        pass

    @abstractproperty
    def timeout(self):
        pass

    @abstractproperty
    def start_period(self):
        pass

    @abstractproperty
    def start_interval(self):
        pass

    @abstractproperty
    def retries(self):
        pass

    def __repr__(self):
        return (
            "ConfigurationHealthcheck("
            f"interval={self.interval},"
            f"timeout={self.timeout},"
            f"start_period={self.start_period},"
            f"start_interval={self.start_interval},"
            f"retries={self.retries}"
            ")"
        )
