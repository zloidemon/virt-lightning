import json

from virt_lightning.image_oci_basic_description import OCIBasicDescription
from virt_lightning.image_oci_media_type import OCIMediaType


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
