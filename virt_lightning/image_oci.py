import json
from datetime import datetime
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


class OCIMediaType:
    def __init__(self, data):
        self.__aux = None

        _, path = data.split("/")

        if "+" in data:
            path, self.__aux = path.split("+")

        self.__parsed = path.split(".")

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
        return (
            "MediaType("
            f"version={self.version},provider={self.provider.value},"
            f"subject={self.subject.value},type={self.type.value}"
            ")"
        )


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


class OCIIndex:
    def __init__(self, data):
        self.__data = json.loads(data)

    @property
    def schema_version(self):
        return self.__data["schemaVersion"]

    @property
    def media_type(self):
        return OCIMediaType(self.__data["mediaType"])

    @property
    def artifact_type(self):
        return self.__data.get("artifactType")

    @property
    def manifests(self):
        return [OCIBlobManifest(manifest) for manifest in self.__data["manifests"]]

    @property
    def subject(self):
        return self.__data.get("subject")

    @property
    def annotations(self):
        return self.__data.get("annotations")

    def __str__(self):
        return f"Index(schemaVersion={self.schema_version},mediaType={self.media_type})"


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


class OCIManifest:
    def __init__(self, data):
        self.__data = json.loads(data)

    @property
    def schema_version(self):
        return self.__data["schemaVersion"]

    @property
    def config(self):
        return OCIBasicDescription(self.__data["config"])

    @property
    def layers(self):
        return [OCIBasicDescription(layer) for layer in self.__data["layers"]]

    @property
    def media_type(self):
        return OCIMediaType(self.__data["mediaType"])

    def __str__(self):
        return f"Manifest(version={self.schema_version})"


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
