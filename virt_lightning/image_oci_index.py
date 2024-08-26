from virt_lightning.image_oci_annotations import OCI_IMAGE_ANNOTATIONS
from virt_lightning.image_oci_content_descriptor import OCIContentDescriptor
from virt_lightning.image_oci_media_type import OCIMediaType
from virt_lightning.image_oci_os import OCIOSDescription


#
#  NOTE: Расширенная реализация класса Descriptor, для Index. По документации
#        надо иметь дополнительные поля.
#
class OCIIndexContentDescriptor(OCIContentDescriptor, OCIOSDescription):
    def __init__(self, data):
        self.__data = data
        OCIContentDescriptor.__init__(self, data)
        OCIOSDescription.__init__(self, data)

    @property
    def platform(self):
        if self.__data.get("platform"):
            return OCIOSDescription(self.__data["platform"])
        return None


class OCIIndex:
    def __init__(self, data):
        self.__data = data

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
        return [
            OCIIndexContentDescriptor(manifest) for manifest in self.__data["manifests"]
        ]

    @property
    def subject(self):
        return self.__data.get("subject")

    @property
    def annotations(self):
        annotations = {}

        #
        # NOTE: Удалем все что не по спецификации для org.opencontainers
        #
        if self.__data.get("annotations"):
            for key, value in self.__data.get("annotations").items():
                match (key.startswith("org.opencontainers")):
                    case True if key not in OCI_IMAGE_ANNOTATIONS:
                        continue
                    case _:
                        annotations.update({key: value})

        return annotations

    def __str__(self):
        return f"Index(schemaVersion={self.schema_version},mediaType={self.media_type})"
