from virt_lightning.image_oci_media_type import OCIMediaType


class OCIBlobManifest:
    def __init__(self, data):
        self.__data = data

    @property
    def digest(self):
        algo, hsum = self.__data["digest"].split(":")
        return (algo, hsum)

    @property
    def size(self):
        return self.__data["size"]

    @property
    def annotations(self):
        return self.__data["annotations"]

    @property
    def media_type(self):
        return OCIMediaType(self.__data["mediaType"])

    def __str__(self):
        return f"BlobManifest(digest={self.size})"
