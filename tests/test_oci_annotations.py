import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_index import OCIIndex


class TestOCIAnnotationsIndexWithManifests(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_index_aux.json").open() as fh:
            self.index = OCIIndex(fh.read())

    def test_annotations_index(self):
        self.assertEqual(
            self.index.annotations["com.example.index.revision"],
            "r124356"
        )

    def test_annotations_manifest_oci(self):
        manifest = self.index.manifests[0]
        self.assertEqual(
            manifest.annotations["org.opencontainers.image.ref.name"],
            "stable-release"
        )

        manifest = self.index.manifests[1]
        self.assertEqual(
            manifest.annotations["org.opencontainers.image.ref.name"],
            "v1.0"
        )

    def test_annotations_manifst_custom(self):
        manifest = self.index.manifests[2]
        self.assertEqual(
            manifest.annotations["org.freedesktop.specifications.metainfo.version"],
            "1.0"
        )
        self.assertEqual(
            manifest.annotations["org.freedesktop.specifications.metainfo.type"],
            "AppStream"
        )


class TestOCIAnnotationsIndexWithCustom(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_index_multiple.json").open() as fh:
            self.index = OCIIndex(fh.read())

    def test_annotations_index_custom(self):
        self.assertEqual(self.index.annotations["com.example.key1"], "value1")
        self.assertEqual(self.index.annotations["com.example.key2"], "value2")


class TestOCIAnnotationsIndexWithWrong(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/image_index_wrong_annotations.json").open() as fh:
            self.index = OCIIndex(fh.read())

    def test_annotations_index_custom(self):
        self.assertEqual(self.index.annotations["com.example.key2"], "value2")

    def test_annotations_manifest_custom(self):
        self.assertGreater(len(self.index.manifests), 0)
        self.assertEqual(len(self.index.manifests), 1)
        self.assertEqual(
            self.index.manifests[0].annotations["com.example.key1"],
            "value1"
        )
