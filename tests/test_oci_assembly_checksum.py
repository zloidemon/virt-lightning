import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_create import OCIImageAssembly


class TestOCIAssemblyImageValidateChecksum(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.source_path = PosixPath("tests/oci_data/" + self.image_name)
        self.assembly = OCIImageAssembly(self.source_path)

    def test_none(self):
        with self.assertRaises(NotImplementedError):
            self.assembly._OCIImageAssembly__calc_checksum("test", None)

    def test_sha256(self):
        self.assertEqual(
            self.assembly._OCIImageAssembly__calc_checksum("test", "sha256"),
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )

    def test_sha512(self):
        self.assertEqual(
            self.assembly._OCIImageAssembly__calc_checksum("test", "sha512"),
            "ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db2"
            "7ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff"
        )
