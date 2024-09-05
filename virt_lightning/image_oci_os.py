from virt_lightning.consts import OperationSystem


#
# NOTE: Общий класс с получением информации об ОС
#
class OCIOSDescription:
    def __init__(self, data):
        self.__data = data

    @property
    def architecture(self):
        return self.__data["architecture"]

    @property
    def os(self):
        return OperationSystem(self.__data["os"])

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
    def features(self):
        raise NotImplementedError("RESERVED for future versions of the specification")
