from virt_lightning.consts import HashingAlgorithm
from virt_lightning.image_oci_media_type import OCIMediaType


class OCIContentDescriptor:
    def __init__(self, data):
        self.__data = data

    @property
    def media_type(self):
        return OCIMediaType(self.__data["mediaType"])

    @property
    def digest(self):
        algo, hsum = self.__data["digest"].split(":")
        return (HashingAlgorithm(algo), hsum)

    @property
    def size(self):
        return self.__data["size"]

    @property
    def urls(self):
        return self.__data.get("urls", [])

    @property
    def annotations(self):
        return self.__data.get("annotations", {})

    @property
    def data(self):
        return self.__data.get("data", None)

    @property
    def artifact_type(self):
        return self.__data.get("artifactType", None)

    def __str__(self):
        return f"Description(digest={self.size})"
