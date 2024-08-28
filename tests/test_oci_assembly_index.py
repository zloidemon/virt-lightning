import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_create import OCIImageAssembly
from virt_lightning.image_oci_index import OCIIndex


class TestOCIAssemblyImageValidateIndex(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.source_path = PosixPath("tests/oci_data/" + self.image_name)
        self.assembly = OCIImageAssembly(self.source_path)
        self.index_data = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "manifests": [
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": ":".join([
                        "sha256",
                        "32a00402fcbc25e58e8f89ffa1197c1eed38f1e0171d3320a1d70bffeda2fda1"
                    ]),
                    "size": 288
                }
            ]
        }

    def test_invalid_media_type_field(self):
        index_data = self.index_data
        index_data["mediaType"] = "application/xml"
        index = OCIIndex(index_data)

        self.assembly._OCIImageAssembly__index_file = index

        self.assertFalse(self.assembly.validate())

    def test_invalid_media_type_entry(self):
        index_data = self.index_data
        index_data["mediaType"] = "application/vnd.oci.image.config.v1+json"
        index = OCIIndex(index_data)

        self.assembly._OCIImageAssembly__index_file = index

        self.assertFalse(self.assembly.validate())

    def test_invalid_manifests_len(self):
        index_data = self.index_data
        index_data["manifests"] = []
        index = OCIIndex(index_data)

        self.assembly._OCIImageAssembly__index_file = index
        self.assertFalse(self.assembly.validate())
