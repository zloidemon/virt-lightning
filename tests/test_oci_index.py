import unittest
from pathlib import PosixPath

from virt_lightning.image_oci import OCIIndex


class TestOCIIndex(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_index.json").open() as fh:
            self.index = OCIIndex(fh.read())

    def test_schema_version(self):
        self.assertEqual(self.index.schema_version, 2)

    def test_media_type(self):
        self.assertEqual(self.index.media_type.provider.value, "oci")
        self.assertEqual(self.index.media_type.subject.value, "image")
        self.assertEqual(self.index.media_type.entry.value, "index")
        self.assertEqual(self.index.media_type.version, "v1")
        self.assertEqual(self.index.media_type.extension, "json")

    def test_artifact_type(self):
        self.assertIsNone(self.index.artifact_type)

    def test_manifests(self):
        self.assertIsNot(len(self.index.manifests), 0)
        self.assertGreater(len(self.index.manifests), 0)
        self.assertEqual(len(self.index.manifests), 2)

    def test_subject(self):
        self.assertIsNone(self.index.subject)

    def test_annotations(self):
        test_dict = {
            "com.example.key1": "value1",
            "com.example.key2": "value2",
        }
        self.assertIsNotNone(self.index.annotations)
        self.assertDictEqual(self.index.annotations, test_dict)



class TestOCIIndexMultiple(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_index_multiple.json").open() as fh:
            self.index = OCIIndex(fh.read())

    def test_schema_version(self):
        self.assertEqual(self.index.schema_version, 2)

    def test_media_type(self):
        self.assertEqual(self.index.media_type.provider.value, "oci")
        self.assertEqual(self.index.media_type.subject.value, "image")
        self.assertEqual(self.index.media_type.entry.value, "index")
        self.assertEqual(self.index.media_type.version, "v1")
        self.assertEqual(self.index.media_type.extension, "json")

    def test_artifact_type(self):
        self.assertIsNone(self.index.artifact_type)

    def test_manifests(self):
        self.assertIsNot(len(self.index.manifests), 0)
        self.assertGreater(len(self.index.manifests), 0)
        self.assertEqual(len(self.index.manifests), 2)

    def test_subject(self):
        self.assertIsNone(self.index.subject)

    def test_annotations(self):
        test_dict = {
            "com.example.key1": "value1",
            "com.example.key2": "value2",
        }
        self.assertIsNotNone(self.index.annotations)
        self.assertDictEqual(self.index.annotations, test_dict)
