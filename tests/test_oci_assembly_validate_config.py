import json
import unittest
from pathlib import PosixPath
from unittest.mock import Mock

from virt_lightning.image_oci_content_descriptor import OCIContentDescriptor
from virt_lightning.image_oci_create import OCIImageAssembly


class TestOCIAssemblyImageValidateConfig(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.source_path = PosixPath("tests/oci_data/" + self.image_name)
        self.assembly = OCIImageAssembly(self.source_path)
        self.config_data = {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": ":".join(
                [
                    "sha256",
                    "65b7ca76e09ec341a1c607b731cebc303e796d7a415ebca1509fdc1f3080614c",
                ]
            ),
            "size": 482,
        }

    def test_valid_config(self):
        validate_config = self.assembly._OCIImageAssembly__validate_config
        config_descriptor = OCIContentDescriptor(self.config_data)
        self.assertTrue(validate_config(config_descriptor))

    def test_invalid_size(self):
        validate_config = self.assembly._OCIImageAssembly__validate_config
        config_data = self.config_data
        config_data["size"] = 483
        config_descriptor = OCIContentDescriptor(config_data)
        self.assertFalse(validate_config(config_descriptor))

    def test_invalid_media_type_entry(self):
        validate_config = self.assembly._OCIImageAssembly__validate_config
        config_data = self.config_data
        config_data["mediaType"] = "application/vnd.oci.image.manifest.v1+json"
        config_descriptor = OCIContentDescriptor(config_data)
        self.assertFalse(validate_config(config_descriptor))

    def test_invalid_media_type_field(self):
        validate_config = self.assembly._OCIImageAssembly__validate_config
        config_data = self.config_data
        config_data["mediaType"] = "application/xml"
        config_descriptor = OCIContentDescriptor(config_data)
        self.assertFalse(validate_config(config_descriptor))

    def test_invalid_not_found(self):
        validate_config = self.assembly._OCIImageAssembly__validate_config
        config_data = self.config_data
        config_data["digest"] = (
            "sha256"
            ":"
            "abc7ca76e09ec341a1c607b731cebc303e796d7a415ebca1509fdc1f3080614c"
        )
        config_descriptor = OCIContentDescriptor(config_data)
        self.assertFalse(validate_config(config_descriptor))

    def test_invalid_hash(self):
        validate_config = self.assembly._OCIImageAssembly__validate_config
        mock_checksum_file = Mock(return_value=("x", ""))
        self.assembly._OCIImageAssembly__load_file = mock_checksum_file

        config_descriptor = OCIContentDescriptor(self.config_data)
        self.assertFalse(validate_config(config_descriptor))

    def test_invalid_json_str(self):
        validate_config = self.assembly._OCIImageAssembly__validate_config
        mock_checksum_file = Mock(
            return_value=(self.config_data["digest"].split(":")[1], "{")
        )
        self.assembly._OCIImageAssembly__load_file = mock_checksum_file

        config_descriptor = OCIContentDescriptor(self.config_data)
        with self.assertRaises(json.decoder.JSONDecodeError):
            validate_config(config_descriptor)
