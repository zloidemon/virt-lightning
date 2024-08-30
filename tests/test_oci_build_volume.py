import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageExpose(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_valid(self):
        vol_0 = PosixPath("/abc")
        vol_1 = PosixPath("/cfd")
        vol_2 = PosixPath("/")

        self.builder.volume(vol_0, vol_1, vol_2)
        self.assertSetEqual(set({vol_0, vol_1, vol_2}), self.builder._OCIImageBuild__volumes)

    def test_duplicate(self):
        self.builder.volume(PosixPath("/"))

        with self.assertRaises(KeyError):
            self.builder.volume(PosixPath("/"))

    def test_empty(self):
        with self.assertRaises(KeyError):
            self.builder.volume()

    def test_invalid_type(self):
        with self.assertRaises(TypeError):
            self.builder.volume("/")

        with self.assertRaises(TypeError):
            self.builder.volume(None)

        with self.assertRaises(TypeError):
            self.builder.volume([None])

        with self.assertRaises(TypeError):
            self.builder.volume(["/"])

        with self.assertRaises(TypeError):
            self.builder.volume("/", PosixPath("/"))

        with self.assertRaises(TypeError):
            self.builder.volume([])

        with self.assertRaises(TypeError):
            self.builder.volume([], [])
