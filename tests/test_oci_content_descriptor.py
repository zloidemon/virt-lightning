import json
import unittest
from pathlib import PosixPath

from virt_lightning.consts import HashingAlgorithm
from virt_lightning.image_oci_content_descriptor import OCIContentDescriptor
from virt_lightning.image_oci_media_type import ImageEnumEntry, ImageEnumSubject


class TestOCIContentDescriptorManifest(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/content_descriptor_manifest.json").open() as fh:
            self.manifest = OCIContentDescriptor(json.loads(fh.read()))

    def test_media_type(self):
        self.assertEqual(ImageEnumSubject.image, self.manifest.media_type.subject)
        self.assertEqual(ImageEnumEntry.manifest, self.manifest.media_type.entry)

    def test_digest(self):
        valid_tuple = (
            HashingAlgorithm.SHA256,
            "5b0bcabd1ed22e9fb1310cf6c2dec7cdef19f0ad69efa1f392e94a4333501270",
        )
        self.assertTupleEqual(valid_tuple, self.manifest.digest)

    def test_size(self):
        self.assertEqual(7682, self.manifest.size)

    def test_repr(self):
        self.assertEqual(repr(self.manifest), "Description(digest=7682)")


class TestOCIContentDescriptorManifestURL(TestOCIContentDescriptorManifest):
    def setUp(self):
        with PosixPath(
            "tests/oci_data/content_descriptor_manifest_url.json"
        ).open() as fh:
            self.manifest = OCIContentDescriptor(json.loads(fh.read()))

    def test_urls(self):
        self.assertListEqual(
            ["https://example.com/example-manifest"], self.manifest.urls
        )


class TestOCIContentDescriptorManifestArtifact(TestOCIContentDescriptorManifest):
    def setUp(self):
        with PosixPath(
            "tests/oci_data/content_descriptor_manifest_artifact.json"
        ).open() as fh:
            self.manifest = OCIContentDescriptor(json.loads(fh.read()))

    def test_media_type(self):
        self.assertEqual(ImageEnumSubject.image, self.manifest.media_type.subject)
        self.assertEqual(ImageEnumEntry.manifest, self.manifest.media_type.entry)

    def test_digest(self):
        valid_tuple = (
            HashingAlgorithm.SHA256,
            "87923725d74f4bfb94c9e86d64170f7521aad8221a5de834851470ca142da630",
        )
        self.assertTupleEqual(valid_tuple, self.manifest.digest)

    def test_size(self):
        self.assertEqual(123, self.manifest.size)

    def test_artifact_type(self):
        self.assertEqual("application/vnd.example.sbom.v1", self.manifest.artifact_type)

    def test_repr(self):
        self.assertEqual(repr(self.manifest), "Description(digest=123)")


class TestOCIContentDescriptorManifestOptional(TestOCIContentDescriptorManifest):
    def test_artifact_type(self):
        self.assertIsNone(self.manifest.artifact_type)

    def test_data(self):
        self.assertIsNone(self.manifest.data)

    def test_annotations(self):
        self.assertDictEqual({}, self.manifest.annotations)

    def test_urls(self):
        self.assertListEqual([], self.manifest.urls)
