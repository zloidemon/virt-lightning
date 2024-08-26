import json
import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_layout import OCIImageLayout


class TestOCIImageLayout(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/oci-layout").open() as fh:
            self.layout = OCIImageLayout(json.loads(fh.read()))

    def test_version(self):
        self.assertIsNotNone(self.layout.version)
        self.assertEqual(self.layout.version, "1.0.0")
        self.assertNotEqual(self.layout.version, "")
