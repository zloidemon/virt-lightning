import json
import unittest
from pathlib import PosixPath
from unittest.mock import Mock

from virt_lightning.image_oci_content_descriptor import OCIContentDescriptor
from virt_lightning.image_oci_create import OCIImageAssembly


class TestOCIAssemblyImageValidateManifest(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.source_path = PosixPath("tests/oci_data/" + self.image_name)
        self.assembly = OCIImageAssembly(self.source_path)
        self.manifest_data = {
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "digest": "sha256:32a00402fcbc25e58e8f89ffa1197c1eed38f1e0171d3320a1d70bffeda2fda1",
            "size": 288
        }

    def test_valid_manifest(self):
        validate_manifest = self.assembly._OCIImageAssembly__validate_manifest
        mock_validate_config = Mock(return_value=True)
        self.assembly._OCIImageAssembly__validate_config = mock_validate_config

        manifest_descriptor = OCIContentDescriptor(self.manifest_data)
        self.assertTrue(validate_manifest(manifest_descriptor))

    def test_invalid_media_type_field(self):
        validate_manifest = self.assembly._OCIImageAssembly__validate_manifest
        manifest_data = self.manifest_data
        manifest_data["mediaType"] = "application/xml"
        manifest_descriptor = OCIContentDescriptor(manifest_data)
        self.assertFalse(validate_manifest(manifest_descriptor))

    def test_invalid_media_type_entry(self):
        validate_manifest = self.assembly._OCIImageAssembly__validate_manifest
        manifest_data = self.manifest_data
        manifest_data["mediaType"] = "application/vnd.oci.image.config.v1+json"
        manifest_descriptor = OCIContentDescriptor(manifest_data)
        self.assertFalse(validate_manifest(manifest_descriptor))

    def test_invalid_not_found(self):
        validate_manifest = self.assembly._OCIImageAssembly__validate_manifest
        manifest_data = self.manifest_data
        manifest_data["digest"] = ":".join([
            "sha256",
            "abc00402fcbc25e58e8f89ffa1197c1eed38f1e0171d3320a1d70bffeda2fda1",
        ])
        manifest_descriptor = OCIContentDescriptor(manifest_data)
        self.assertFalse(validate_manifest(manifest_descriptor))

    def test_invalid_hash(self):
        validate_manifest = self.assembly._OCIImageAssembly__validate_manifest
        mock_checksum_file = Mock(return_value=("x", ""))
        self.assembly._OCIImageAssembly__load_file = mock_checksum_file

        manifest_descriptor = OCIContentDescriptor(self.manifest_data)
        self.assertFalse(validate_manifest(manifest_descriptor))

    def test_invalid_size(self):
        validate_manifest = self.assembly._OCIImageAssembly__validate_manifest
        manifest_data = self.manifest_data
        manifest_data["size"] = 77
        manifest_descriptor = OCIContentDescriptor(manifest_data)
        self.assertFalse(validate_manifest(manifest_descriptor))

    def test_invalid_json_str(self):
        validate_manifest = self.assembly._OCIImageAssembly__validate_manifest
        mock_checksum_file = Mock(return_value=(self.manifest_data["digest"].split(":")[1], "{"))
        self.assembly._OCIImageAssembly__load_file = mock_checksum_file

        manifest_descriptor = OCIContentDescriptor(self.manifest_data)
        with self.assertRaises(json.decoder.JSONDecodeError):
            validate_manifest(manifest_descriptor)
