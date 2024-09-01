import unittest

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageCmd(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.builder.cmd(None)
