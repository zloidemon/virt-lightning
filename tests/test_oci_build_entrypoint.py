import unittest

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageEntrypoint(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.builder.entrypoint(None)
