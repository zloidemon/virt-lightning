import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_index import OCIIndex
from virt_lightning.image_oci_media_type import OCIMediaType

TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_CONTENT_DESCRIPTOR = "application/vnd.oci.descriptor.v1+json"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_OCI_LAYOUT = "application/vnd.oci.layout.header.v1+json"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_INDEX = "application/vnd.oci.image.index.v1+json"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_MANIFEST = "application/vnd.oci.image.manifest.v1+json"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_CONFIG = "application/vnd.oci.image.config.v1+json"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_LAYER = "application/vnd.oci.image.layer.v1.tar"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_LAYER_GZIP = "application/vnd.oci.image.layer.v1.tar+gzip"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_LAYER_ZSTD = "application/vnd.oci.image.layer.v1.tar+zstd"
TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_EMPTY = "application/vnd.oci.empty.v1+json"


class TestOCIMediaType(unittest.TestCase):
    def setUp(self):
        self.content_descriptor = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_CONTENT_DESCRIPTOR)
        self.oci_layout = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_OCI_LAYOUT)
        self.image_index = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_INDEX)
        self.image_manifest = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_MANIFEST)
        self.image_config = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_CONFIG)
        self.layer = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_LAYER)
        self.layer_gzip = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_LAYER_GZIP)
        self.layer_zstd = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_LAYER_ZSTD)
        self.empty = OCIMediaType(TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_EMPTY)

    def is_oci(self):
        self.assertIsTrue(self.content_descriptor.is_oci())
        self.assertIsTrue(self.oci_layout.is_oci())
        self.assertIsTrue(self.image_index.is_oci())
        self.assertIsTrue(self.image_manifest.is_oci())
        self.assertIsTrue(self.image_config.is_oci())
        self.assertIsTrue(self.layer.is_oci())
        self.assertIsTrue(self.layer_gzip.is_oci())
        self.assertIsTrue(self.layer_zstd.is_oci())
        self.assertIsTrue(self.layer_empty.is_oci())
        self.assertIsFalse(OCIMediaType("application/xml").is_oci())

    def test_content_descriptor(self):
        self.assertEqual(self.content_descriptor.version, "v1")
        self.assertEqual(self.content_descriptor.provider.value, "oci")
        self.assertEqual(self.content_descriptor.subject.value, "descriptor")
        self.assertIsNone(self.content_descriptor.entry)
        self.assertIsNone(self.content_descriptor.extension)

    def test_oci_layout(self):
        self.assertEqual(self.oci_layout.version, "v1")
        self.assertEqual(self.oci_layout.provider.value, "oci")
        self.assertEqual(self.oci_layout.subject.value, "layout")
        self.assertEqual(self.oci_layout.entry.value, "header")
        self.assertEqual(self.oci_layout.extension, "json")

    def test_image_index(self):
        self.assertEqual(self.image_index.version, "v1")
        self.assertEqual(self.image_index.provider.value, "oci")
        self.assertEqual(self.image_index.subject.value, "image")
        self.assertEqual(self.image_index.entry.value, "index")
        self.assertEqual(self.image_index.extension, "json")

    def test_image_manifest(self):
        self.assertEqual(self.image_manifest.version, "v1")
        self.assertEqual(self.image_manifest.provider.value, "oci")
        self.assertEqual(self.image_manifest.subject.value, "image")
        self.assertEqual(self.image_manifest.entry.value, "manifest")
        self.assertEqual(self.image_manifest.extension, "json")

    def test_image_config(self):
        self.assertEqual(self.image_config.version, "v1")
        self.assertEqual(self.image_config.provider.value, "oci")
        self.assertEqual(self.image_config.subject.value, "image")
        self.assertEqual(self.image_config.entry.value, "config")
        self.assertEqual(self.image_config.extension, "json")

    def test_layer(self):
        self.assertEqual(self.layer.version, "v1")
        self.assertEqual(self.layer.provider.value, "oci")
        self.assertEqual(self.layer.subject.value, "image")
        self.assertEqual(self.layer.entry.value, "layer")
        self.assertEqual(self.layer.extension, "tar")

    def test_layer_gzip(self):
        self.assertEqual(self.layer_gzip.version, "v1")
        self.assertEqual(self.layer_gzip.provider.value, "oci")
        self.assertEqual(self.layer_gzip.subject.value, "image")
        self.assertEqual(self.layer_gzip.entry.value, "layer")
        self.assertEqual(self.layer_gzip.extension, "tar.gzip")

    def test_layer_zstd(self):
        self.assertEqual(self.layer_zstd.version, "v1")
        self.assertEqual(self.layer_zstd.provider.value, "oci")
        self.assertEqual(self.layer_zstd.subject.value, "image")
        self.assertEqual(self.layer_zstd.entry.value, "layer")
        self.assertEqual(self.layer_zstd.extension, "tar.zstd")

    def test_empty(self):
        self.assertEqual(self.empty.version, "v1")
        self.assertEqual(self.empty.provider.value, "oci")
        self.assertEqual(self.empty.subject.value, "empty")
        self.assertIsNone(self.empty.entry)
        self.assertEqual(self.empty.extension, "json")


class TestOCIMediaTypeCustom(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_index_aux.json").open() as fh:
            self.index = OCIIndex(fh.read())

    def test_str(self):
        manifest = self.index.manifests[0]
        self.assertIsNotNone(manifest.media_type)
        self.assertEqual(
            str(manifest.media_type),
            TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_INDEX,
        )
        manifest = self.index.manifests[1]
        self.assertIsNotNone(manifest.media_type)
        self.assertEqual(
            str(manifest.media_type),
            TEST_SUITE_OCI_IMAGE_MEDIA_TYPE_IMAGE_MANIFEST,
        )
        manifest = self.index.manifests[2]
        self.assertIsNotNone(manifest.media_type)
        self.assertEqual(str(manifest.media_type), "application/xml")
        self.assertGreater(manifest.size, 0)
        self.assertEqual(manifest.size, 7143)
