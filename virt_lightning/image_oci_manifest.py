import json

from virt_lightning.image_oci_content_descriptor import OCIContentDescriptor
from virt_lightning.image_oci_media_type import OCIMediaType


class OCIManifest:
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
    def config(self):
        return OCIContentDescriptor(self.__data["config"])

    @property
    def layers(self):
        return [OCIContentDescriptor(layer) for layer in self.__data["layers"]]

    @property
    def subject(self):
        if self.__data.get("subject"):
            return OCIContentDescriptor(self.__data["subject"])
        return None

    @property
    def annotations(self):
        return self.__data.get("annotations", {})

    def __str__(self):
        return f"Manifest(version={self.schema_version})"
