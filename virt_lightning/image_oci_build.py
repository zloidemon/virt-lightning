from pathlib import PosixPath

from virt_lightning.configuration_healthcheck import ConfigurationHealthcheck
from virt_lightning.configuration_posix_user import ConfigurationPosixUser
from virt_lightning.consts import NetworkProtocolTCPIP, SignalShutdown
from virt_lightning.healthcheck import Healthcheck


class OCIImageBuild:
    def __init__(self, name):
        self.__name = name
        self.__labels = {}
        self.__env = {}
        self.__ports = set({})
        self.__volumes = set({})
        self.__healthcheck = None
        self.__workdir = None
        self.__user = None
        self.__stopsignal = None

    # --keep-git-dir
    # --checksum
    # --chown
    # --chmod
    # --link
    # --exclude
    def add(self, src, dst):
        return self

    def arg(self, key, value):
        return self

    #
    # FIXME: Подумать как это сделать, а может и не нужно
    #
    def cmd(self, *args):
        raise NotImplementedError("not known how it should work")

    # --from
    # --chown
    # --chmod
    # --link
    # --parents
    # --exclude
    def copy(self, src, dst):
        return self

    #
    # FIXME: Подумать как это сделать, а может и не нужно
    #
    def entrypoint(self, entry):
        raise NotImplementedError("not known how it should work")

    def env(self, key, value):
        if not isinstance(key, str):
            raise TypeError("key must be string")

        if len(key) == 0 or key == "":
            raise ValueError("key must be none zero string")

        if not isinstance(value, str):
            raise TypeError("value must be string")

        self.__env[key] = value

        return self

    def expose(self, port, protocol="tcp"):
        _protocol = NetworkProtocolTCPIP(protocol)

        if not isinstance(port, int):
            raise TypeError("port must be integer in range 0 .. 65535")

        if port < 0 or port > 65535:
            raise ValueError("port is out of range 0 .. 65535")

        record = f"{port}/{_protocol.value}"

        if len(self.__ports & set({record})):
            raise KeyError(f"{record}: already allocated")
        else:
            self.__ports.update({record})

        return self

    # --platform
    # def from(self):
    #    return self

    def healthcheck(
        self, cmd, interval=30, timeout=30, start_period=0, start_interval=5, retries=3
    ):
        if self.__healthcheck:
            raise KeyError("healthcheck already defined")

        if not isinstance(cmd, str):
            raise TypeError("cmd must be string to executable file")

        if len(cmd) < 1 or cmd == "":
            raise ValueError("cmd can not be empty string")

        for option in [interval, timeout, start_period, start_interval, retries]:
            if not isinstance(option, int):
                raise TypeError("options healthcheck must be integers")

            if option < 0:
                raise ValueError("options can not be negative")

        configuration = ConfigurationHealthcheck()

        configuration.interval = interval
        configuration.timeout = timeout
        configuration.start_period = start_period
        configuration.start_interval = start_interval
        configuration.retries = retries

        self.__healthcheck = Healthcheck(cmd, configuration)

        return self

    def label(self, key, value):
        if not isinstance(key, str):
            raise TypeError("key must be string")

        if len(key) == 0 or key == "":
            raise ValueError("key must be none zero string")

        if not isinstance(value, str):
            raise TypeError("value must be string")

        if not self.__labels.get(key, None):
            self.__labels[key] = value
        else:
            raise KeyError(f"'{key}' already exists with value: '{self.__labels[key]}'")
        return self

    def onbuilt(self, callback):
        return self

    # --mount
    # --network
    # --security
    def run(self):
        return self

    def shell(self, filename, *args):
        return self

    def stopsignal(self, signal):
        if not isinstance(signal, SignalShutdown):
            raise TypeError("stop signal must be SignalShutdown")

        if self.__stopsignal:
            raise KeyError(f"stop signal {self.__stopsignal.value} already defined")

        self.__stopsignal = signal

        return self

    def user(self, user):
        if not isinstance(user, ConfigurationPosixUser):
            raise TypeError("user must be ConfigurationPosixUser")

        self.__user = user

        return self

    def volume(self, *args):
        if len(args) < 1:
            raise KeyError("must have more volumes in arguments")

        for volume in args:
            if not isinstance(volume, PosixPath):
                raise TypeError("volume must be PosixPath")

            if len(self.__volumes & set({volume})):
                raise KeyError(f"volume '{str(volume)}': already defined")
            else:
                self.__volumes.update({volume})
        return self

    def workdir(self, path):
        if not isinstance(path, PosixPath):
            raise TypeError("workdir must be PosixPath")
        if self.__workdir:
            self.__workdir = self.__workdir / path
        else:
            if path.root == "/":
                self.__workdir = path
            else:
                raise ValueError("workdir must starts with '/'")

        return self
