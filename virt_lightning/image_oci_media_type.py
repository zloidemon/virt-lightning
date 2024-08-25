from enum import Enum, unique


@unique
class ImageEnumProvider(Enum):
    docker = "docker"
    oci = "oci"


@unique
class ImageEnumSubject(Enum):
    descriptor = "descriptor"
    empty = "empty"
    image = "image"
    layout = "layout"


@unique
class ImageEnumEntry(Enum):
    config = "config"
    header = "header"
    index = "index"
    layer = "layer"
    manifest = "manifest"


OCI_MEDIA_TYPES = [
    "application/vnd.oci.descriptor.v1+json",
    "application/vnd.oci.layout.header.v1+json",
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.oci.image.config.v1+json",
    "application/vnd.oci.image.layer.v1.tar",
    "application/vnd.oci.image.layer.v1.tar+gzip",
    "application/vnd.oci.image.layer.v1.tar+zstd",
    "application/vnd.oci.empty.v1+json",
]


class OCIMediaType:
    def __init__(self, data):
        self.__aux = None
        self.__data = data

        _, path = data.split("/")

        if "+" in data:
            path, self.__aux = path.split("+")

        self.__parsed = path.split(".")

    def is_oci(self):
        if self.__data not in OCI_MEDIA_TYPES:
            return False
        return True

    @property
    def provider(self):
        return ImageEnumProvider(self.__parsed[1])

    @property
    def subject(self):
        return ImageEnumSubject(self.__parsed[2])

    @property
    def entry(self):
        match self.subject:
            case ImageEnumSubject.image | ImageEnumSubject.layout:
                return ImageEnumEntry(self.__parsed[3])
            case _:
                return None

    @property
    def extension(self):
        match (self.subject, self.entry):
            case (
                _,
                ImageEnumEntry.config | ImageEnumEntry.index | ImageEnumEntry.manifest,
            ):
                return self.__aux
            case (ImageEnumSubject.image, ImageEnumEntry.layer):
                if self.__aux:
                    return ".".join([self.__parsed[5], self.__aux])
                return self.__parsed[5]
            case (ImageEnumSubject.layout, ImageEnumEntry.header):
                return self.__aux
            case (ImageEnumSubject.empty, _):
                return self.__aux
            case _:
                return None

    @property
    def version(self):
        match self.subject:
            case ImageEnumSubject.image | ImageEnumSubject.layout:
                return self.__parsed[4]
            case ImageEnumSubject.empty | ImageEnumSubject.descriptor:
                return self.__parsed[3]
            case _:
                raise Exception(f"unsupported type: {self.subject.value}")

    def __str__(self):
        return self.__data
