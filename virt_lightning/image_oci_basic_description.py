from virt_lightning.image_oci_media_type import OCIMediaType


class OCIBasicDescription:
    def __init__(self, data):
        self.__data = data

    @property
    def media_type(self):
        return OCIMediaType(self.__data["mediaType"])

    @property
    def digest(self):
        algo, hsum = self.__data["digest"].split(":")
        return (algo, hsum)

    @property
    def size(self):
        return self.__data["size"]

    def __str__(self):
        return f"Description(digest={self.size})"
