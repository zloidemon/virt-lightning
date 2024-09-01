import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageWorkdir(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_valid_workdir(self):
        self.builder.workdir(PosixPath("/z"))
        self.assertEqual(PosixPath("/z"), self.builder._OCIImageBuild__workdir)

    def test_append_workdir(self):
        self.builder.workdir(PosixPath("/z"))
        self.builder.workdir(PosixPath("f"))
        self.assertEqual(PosixPath("/z/f"), self.builder._OCIImageBuild__workdir)

    def test_wrong_append(self):
        with self.assertRaises(ValueError):
            self.builder.workdir(PosixPath("z"))

    def test_wrong_workdir(self):
        with self.assertRaises(TypeError):
            self.builder.workdir("/")
        with self.assertRaises(TypeError):
            self.builder.workdir(None)
        with self.assertRaises(TypeError):
            self.builder.workdir(1)
