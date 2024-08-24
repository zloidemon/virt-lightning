import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_index import OCIIndex


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



class TestOCIIndexAux(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_index_aux.json").open() as fh:
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
        self.assertEqual(len(self.index.manifests), 3)

    def test_manifest_0(self):
        manifest = self.index.manifests[0]
        self.assertEqual(manifest.media_type.provider.value, "oci")
        self.assertEqual(manifest.media_type.subject.value, "image")
        self.assertEqual(manifest.media_type.entry.value, "index")
        self.assertEqual(manifest.media_type.version, "v1")
        self.assertEqual(manifest.media_type.extension, "json")
        self.assertGreater(manifest.size, 0)
        self.assertEqual(manifest.size, 7143)
        valid_digest = (
            "sha256",
            "0228f90e926ba6b96e4f39cf294b2586d38fbb5a1e385c05cd1ee40ea54fe7fd",
        )
        self.assertTupleEqual(manifest.digest, valid_digest)
        valid_annotations = {
            "org.opencontainers.image.ref.name": "stable-release",
        }
        self.assertDictEqual(manifest.annotations, valid_annotations)

    def test_manifest_1(self):
        manifest = self.index.manifests[1]
        self.assertEqual(manifest.media_type.provider.value, "oci")
        self.assertEqual(manifest.media_type.subject.value, "image")
        self.assertEqual(manifest.media_type.entry.value, "manifest")
        self.assertEqual(manifest.media_type.version, "v1")
        self.assertEqual(manifest.media_type.extension, "json")
        self.assertGreater(manifest.size, 0)
        self.assertEqual(manifest.size, 7143)
        valid_digest = (
            "sha256",
            "e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f",
        )
        self.assertTupleEqual(manifest.digest, valid_digest)
        valid_annotations = {
            "org.opencontainers.image.ref.name": "v1.0",
        }
        self.assertDictEqual(manifest.annotations, valid_annotations)

    def test_subject(self):
        self.assertIsNone(self.index.subject)

    def test_annotations(self):
        test_dict = {
            "com.example.index.revision": "r124356",
        }
        self.assertIsNotNone(self.index.annotations)
        self.assertDictEqual(self.index.annotations, test_dict)
