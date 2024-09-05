from datetime import datetime

from virt_lightning.consts import SignalShutdown
from virt_lightning.image_oci_os import OCIOSDescription


class OCIHistoryRecord:
    def __init__(self, data):
        self.__data = data

    @property
    def empty_layer(self):
        return self.__data.get("empty_layer", False)

    @property
    def author(self):
        return self.__data.get("author", None)

    @property
    def created(self):
        if self.__data.get("created"):
            return datetime.fromisoformat(self.__data["created"])
        return None

    @property
    def comment(self):
        return self.__data.get("comment")

    @property
    def created_by(self):
        return self.__data.get("created_by")

    def __str__(self):
        return (
            f"Record(created_by={len(self.created_by)},empty_layer={self.empty_layer})"
        )


class OCIConfigConfig:
    def __init__(self, data):
        self.__data = data

    @property
    def user(self):
        if self.__data.get("User"):
            return self.__data["User"]
        return None

    @property
    def exposed_ports(self):
        if self.__data.get("ExposedPorts"):
            return self.__data["ExposedPorts"]
        return None

    @property
    def env(self):
        dicted = {}
        if self.__data.get("Env"):
            for field in self.__data["Env"]:
                key, val = field.split("=")
                dicted.update({key: val})
            return dicted
        return None

    @property
    def entrypoint(self):
        if self.__data.get("Entrypoint"):
            return self.__data["Entrypoint"]
        return None

    @property
    def cmd(self):
        if self.__data.get("Cmd"):
            return self.__data["Cmd"]
        return []

    @property
    def volumes(self):
        if self.__data.get("Volumes"):
            return self.__data["Volumes"]
        return None

    @property
    def workingdir(self):
        if self.__data.get("WorkingDir"):
            return self.__data["WorkingDir"]
        return None

    @property
    def labels(self):
        if self.__data.get("Labels"):
            return self.__data["Labels"]
        return {}

    @property
    def stop_signal(self):
        if self.__data.get("StopSignal"):
            return SignalShutdown(self.__data["StopSignal"])
        return None

    @property
    def memory(self):
        if self.__data.get("Memory", None) is not None:
            if self.__data["Memory"] < 1:
                raise ValueError("memory must be greater than 0")
            return self.__data["Memory"]
        return None

    @property
    def memory_swap(self):
        if self.__data.get("MemorySwap", None) is not None:
            if self.__data["MemorySwap"] < 1:
                raise ValueError("memory_swap must be greater than 0")
            return self.__data["MemorySwap"]
        return None

    @property
    def cpu_shares(self):
        if self.__data.get("CpuShares", None) is not None:
            if self.__data["CpuShares"] < 1:
                raise ValueError("cpu_shares must be greater than 0")
            return self.__data["CpuShares"]
        return None

    @property
    def healthcheck(self):
        if self.__data.get("Healthcheck"):
            return self.__data["Healthcheck"]
        return None


class OCIConfigRootfs:
    def __init__(self, data):
        self.__data = data

    @property
    def type(self):  # noqa: A003
        return self.__data["type"]

    @property
    def diff_ids(self):
        data = []
        for record in self.__data["diff_ids"]:
            algo, hsum = record.split(":")
            data.append((algo, hsum))
        return data

    def __str__(self):
        return f"Config(type={self.type},diff_ids={len(self.diff_ids)})"


class OCIConfig(OCIOSDescription):
    def __init__(self, data):
        self.__data = data
        OCIOSDescription.__init__(self, data)

    @property
    def created(self):
        if self.__data.get("created"):
            return datetime.fromisoformat(self.__data["created"])
        return None

    @property
    def author(self):
        if self.__data.get("author"):
            return self.__data["author"]
        return None

    @property
    def config(self):
        if self.__data.get("config"):
            return OCIConfigConfig(self.__data["config"])
        return None

    @property
    def rootfs(self):
        return OCIConfigRootfs(self.__data["rootfs"])

    @property
    def history(self):
        if self.__data.get("history"):
            return [OCIHistoryRecord(record) for record in self.__data["history"]]
        return []

    def __str__(self):
        return f"Config(architecture={self.architecture},os={self.os})"
