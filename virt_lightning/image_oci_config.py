from datetime import datetime


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
        return f"Record(created_by={self.created_by},empty_layer={self.empty_layer})"


class OCIConfigConfig:
    def __init__(self, data):
        self.__data = data

    @property
    def user(self):
        if self.__data.get("user"):
            return self.__data["user"]
        return None

    @property
    def exposed_ports(self):
        if self.__data.get("ExposedPorts"):
            return self.__data["ExposedPorts"]
        return None

    @property
    def env(self):
        if self.__data.get("Env"):
            return self.__data["Env"]
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
        return None

    @property
    def volumes(self):
        if self.__data.get("Volumes"):
            return self.__data["Volumes"]
        return None

    @property
    def working_dir(self):
        if self.__data.get("WorkingDir"):
            return self.__data["WorkingDir"]
        return None

    @property
    def labels(self):
        if self.__data.get("labels"):
            return self.__data["labels"]
        return []

    @property
    def stop_signal(self):
        if self.__data.get("StopSignal"):
            return self.__data["StopSignal"]
        return None

    @property
    def memory(self):
        if self.__data.get("Memory"):
            return self.__data["Memory"]
        return None

    @property
    def memory_swap(self):
        if self.__data.get("MemorySwap"):
            return self.__data["MemorySwap"]
        return None

    @property
    def cpu_shares(self):
        if self.__data.get("CpuShares"):
            return self.__data["CpuShares"]
        return None

    @property
    def healthcheck(self):
        if self.__data.get("Healthcheck"):
            return self.__data["Healthcheck"]
        return None


class OCIConfig:
    def __init__(self, data):
        self.__data = data

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
    def architecture(self):
        return self.__data["architecture"]

    @property
    def os(self):
        return self.__data["os"]

    @property
    def os_version(self):
        return self.__data.get("os.version")

    @property
    def os_features(self):
        if self.__data.get("os.features"):
            return self.__data["os.features"]
        return []

    @property
    def variant(self):
        return self.__data.get("variant")

    @property
    def history(self):
        if self.__data.get("history"):
            return [OCIHistoryRecord(record) for record in self.__data["history"]]
        return []

    @property
    def config(self):
        if self.__data.get("config"):
            return OCIConfigConfig(self.__data["config"])
        return None

    def __str__(self):
        return f"Config(architecture={self.architecture},os={self.os})"
