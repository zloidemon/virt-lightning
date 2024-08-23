import json

from virt_lightning.image_oci_content_descriptor import OCIContentDescriptor
from virt_lightning.image_oci_media_type import OCIMediaType


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
        return [OCIContentDescriptor(manifest) for manifest in self.__data["manifests"]]

    @property
    def subject(self):
        return self.__data.get("subject")

    @property
    def annotations(self):
        return self.__data.get("annotations")

    def __str__(self):
        return f"Index(schemaVersion={self.schema_version},mediaType={self.media_type})"
