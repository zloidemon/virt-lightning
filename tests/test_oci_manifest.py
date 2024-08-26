import json
import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_manifest import OCIManifest


class TestOCIManifest(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_manifest.json").open() as fh:
            self.manifest = OCIManifest(json.loads(fh.read()))

    def test_schema_version(self):
        self.assertEqual(self.manifest.schema_version, 2)

    def test_media_type(self):
        self.assertIsNotNone(self.manifest.media_type)
        self.assertEqual(self.manifest.media_type.version, "v1")
        self.assertEqual(self.manifest.media_type.provider.value, "oci")
        self.assertEqual(self.manifest.media_type.subject.value, "image")
        self.assertEqual(self.manifest.media_type.entry.value, "manifest")
        self.assertEqual(self.manifest.media_type.extension, "json")

    def test_artifact_type(self):
        self.assertIsNone(self.manifest.artifact_type)

    def test_config(self):
        self.assertIsNotNone(self.manifest.config)
        self.assertIsNotNone(self.manifest.config.media_type)
        self.assertEqual(self.manifest.config.media_type.version, "v1")
        self.assertEqual(self.manifest.config.media_type.provider.value, "oci")
        self.assertEqual(self.manifest.config.media_type.subject.value, "image")
        self.assertEqual(self.manifest.config.media_type.entry.value, "config")
        self.assertEqual(self.manifest.config.media_type.extension, "json")
        valid_config_hash = (
            "sha256",
            "b5b2b2c507a0944348e0303114d8d93aaaa081732b86451d9bce1f432a537bc7",
        )
        self.assertTupleEqual(self.manifest.config.digest, valid_config_hash)
        self.assertGreater(self.manifest.config.size, 0)
        self.assertEqual(self.manifest.config.size, 7023)

    def test_layers(self):
        self.assertIsNotNone(self.manifest.layers)
        self.assertGreater(len(self.manifest.layers), 0)
        self.assertEqual(len(self.manifest.layers), 3)

        for idx, layer in enumerate(self.manifest.layers):
            self.assertEqual(layer.media_type.version, "v1")
            self.assertEqual(layer.media_type.provider.value, "oci")
            self.assertEqual(layer.media_type.subject.value, "image")
            self.assertEqual(layer.media_type.entry.value, "layer")
            self.assertEqual(layer.media_type.extension, "tar.gzip")

            match idx:
                case 0:
                    self.assertEqual(layer.size, 32654)
                    self.assertTupleEqual(
                        layer.digest,
                        (
                            "sha256",
                            "9834876dcfb05cb167a5c24953eba58c4ac89b1adf57f28f2f9d09af107ee8f0",
                        )
                    )
                case 1:
                    self.assertEqual(layer.size, 16724)
                    self.assertTupleEqual(
                        layer.digest,
                        (
                            "sha256",
                            "3c3a4604a545cdc127456d94e421cd355bca5b528f4a9c1905b15da2eb4a4c6b",
                        )
                    )
                case 2:
                    self.assertEqual(layer.size, 73109)
                    self.assertTupleEqual(
                        layer.digest,
                        (
                            "sha256",
                            "ec4b8955958665577945c89419d1af06b5f7636b4ac3da7f12184802ad867736",
                        )
                    )

    def test_subject(self):
        self.assertIsNotNone(self.manifest.subject)
        self.assertEqual(self.manifest.subject.media_type.version, "v1")
        self.assertEqual(self.manifest.subject.media_type.provider.value, "oci")
        self.assertEqual(self.manifest.subject.media_type.subject.value, "image")
        self.assertEqual(self.manifest.subject.media_type.entry.value, "manifest")
        self.assertEqual(self.manifest.subject.media_type.extension, "json")

    def test_annotations(self):
        self.assertIsNotNone(self.manifest.annotations)
        valid = {
            "com.example.key1": "value1",
            "com.example.key2": "value2",
        }
        self.assertDictEqual(self.manifest.annotations, valid)
