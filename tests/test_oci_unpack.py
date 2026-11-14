import json
import shutil
import tarfile
import tempfile
import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_create import OCIImageAssembly
from virt_lightning.image_oci_index import OCIIndex
from virt_lightning.image_oci_layout import OCIImageLayout


class TestOCIAssemblyImageUnpack(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.source_path = PosixPath("tests/oci_data/" + self.image_name)
        self.test_dir = PosixPath(tempfile.mkdtemp())
        self.assembly = OCIImageAssembly(self.source_path, self.test_dir)
        self.image_file = PosixPath(self.image_name + ".tar.gz")

    def test_inspect(self):
        index = self.assembly.inspect()
        self.assertEqual(index.schema_version, 2)
        self.assertEqual(len(index.manifests), 1)
        self.assertTrue(index.media_type.is_oci())
        self.assertEqual(index.media_type.entry.value, "index")

    def test_validate(self):
        self.assertTrue(self.assembly.validate())

    def test_tar_read(self):
        self.assembly.make(self.image_file)
        archive = self.test_dir / self.image_file
        self.assertTrue(archive.is_file())
        self.assertTrue(tarfile.is_tarfile(archive))

        with tarfile.open(archive, mode="r") as tar:
            tar_layout = OCIImageLayout(
                json.loads(tar.extractfile("oci-layout").read())
            )
            tar_index = OCIIndex(json.loads(tar.extractfile("index.json").read()))

        self.assertEqual(tar_layout.version, "1.0.0")
        self.assertEqual(tar_index.schema_version, 2)
        self.assertEqual(len(tar_index.manifests), 1)

    def test_private_index(self):
        index = self.assembly._OCIImageAssembly__index
        self.assertIsNotNone(index)
        self.assertIsInstance(index, OCIIndex)

    def test_make(self):
        self.assembly.make(self.image_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir)
